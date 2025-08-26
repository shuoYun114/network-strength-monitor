import requests
import time
import subprocess
import re
import json
import random
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 服务器地址 - 请替换为您的实际服务器IP
SERVER_URL = "http://192.168.1.100:5000/update"  # 示例IP，请修改

def get_network_info_termux():
    """
    使用Termux-API获取手机网络信息
    返回: 包含网络类型和信号强度的字典
    """
    try:
        result = subprocess.run(["termux-telephony-cellinfo"], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout.strip():
            # 检查是否有权限错误
            if "permission" in result.stdout.lower() or "grant" in result.stdout.lower():
                logger.error("需要位置权限，请运行: termux-setup-storage 并授予位置权限")
                return None
                
            try:
                data = json.loads(result.stdout)
                if data and len(data) > 0:
                    # 返回第一个有效小区的信息
                    return data[0]
            except json.JSONDecodeError:
                logger.error("无法解析Termux-API返回的JSON数据")
                return None
                
        return None
        
    except subprocess.TimeoutExpired:
        logger.error("Termux-API命令执行超时")
        return None
    except Exception as e:
        logger.error(f"Termux-API执行出错: {e}")
        return None

def parse_signal_strength(network_info):
    """
    解析网络信息中的信号强度
    根据不同的网络类型使用不同的解析方法
    """
    if not network_info:
        return None
    
    # 尝试直接获取信号强度
    strength = None
    
    # 检查网络类型
    network_type = network_info.get('type', 'unknown').lower()
    
    # 根据不同网络类型解析信号强度
    if 'gsm' in network_type or 'umts' in network_type:
        # GSM/UMTS网络
        if 'dbm' in network_info:
            strength = network_info['dbm']
        elif 'signalStrength' in network_info:
            # GSM信号强度范围: 0-31, 99表示未知
            gsm_strength = network_info['signalStrength']
            if gsm_strength != 99 and 0 <= gsm_strength <= 31:
                # 转换为dBm: -113dBm + 2 * asu
                strength = -113 + 2 * gsm_strength
    
    elif 'lte' in network_type:
        # LTE网络
        if 'dbm' in network_info:
            strength = network_info['dbm']
        elif 'signalStrength' in network_info:
            # LTE信号强度范围: 0-31, 99表示未知
            lte_strength = network_info['signalStrength']
            if lte_strength != 99 and 0 <= lte_strength <= 31:
                # 转换为dBm: -140dBm + asu
                strength = -140 + lte_strength
        elif 'rsrp' in network_info:
            # RSRP (Reference Signal Received Power)
            strength = network_info['rsrp']
    
    elif 'nr' in network_type or '5g' in network_type:
        # 5G NR网络
        if 'dbm' in network_info:
            strength = network_info['dbm']
        elif 'ssRsrp' in network_info:
            # SS-RSRP (Synchronization Signal Reference Signal Received Power)
            strength = network_info['ssRsrp']
    
    elif 'cdma' in network_type:
        # CDMA网络
        if 'dbm' in network_info:
            strength = network_info['dbm']
        elif 'cdmaDbm' in network_info:
            strength = network_info['cdmaDbm']
        elif 'evdoDbm' in network_info:
            strength = network_info['evdoDbm']
    
    # 如果仍未找到信号强度，尝试通用字段
    if strength is None:
        for key in ['dbm', 'signalStrength', 'rssi', 'ss', 'rsrp', 'rsrq', 'rssnr']:
            if key in network_info:
                strength = network_info[key]
                break
    
    return strength

def get_wifi_info():
    """
    获取WiFi连接信息
    返回: 包含WiFi信号强度的字典
    """
    try:
        result = subprocess.run(["termux-wifi-connectioninfo"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                logger.error("无法解析WiFi信息JSON")
                return None
                
        return None
        
    except Exception as e:
        logger.error(f"获取WiFi信息出错: {e}")
        return None

def get_network_strength():
    """
    获取网络信号强度（尝试多种方法）
    返回: 信号强度值(dBm)或网络质量指标
    """
    # 方法1: 使用Termux-API获取蜂窝网络信号
    network_info = get_network_info_termux()
    if network_info:
        strength = parse_signal_strength(network_info)
        if strength is not None:
            network_type = network_info.get('type', 'unknown')
            logger.info(f"获取到{network_type}网络信号强度: {strength} dBm")
            return strength
    
    # 方法2: 获取WiFi信号强度
    wifi_info = get_wifi_info()
    if wifi_info and 'rssi' in wifi_info:
        wifi_strength = wifi_info['rssi']
        logger.info(f"获取到WiFi信号强度: {wifi_strength} dBm")
        return wifi_strength
    
    # 方法3: 获取网络质量指标
    network_quality = get_network_quality()
    if network_quality is not None:
        # 将延迟转换为类似信号强度的值（延迟越低，值越高）
        # 延迟范围: 0-1000ms -> 信号强度范围: -100到-50
        quality_strength = max(-100, min(-50, -50 - (network_quality / 10)))
        logger.info(f"基于网络延迟 {network_quality}ms 计算信号强度: {quality_strength} dBm")
        return quality_strength
    
    # 方法4: 模拟数据(用于测试)
    logger.warning("所有方法都失败，使用模拟数据进行测试")
    return random.randint(-110, -60)

def get_network_quality():
    """
    通过ping测试网络质量
    返回: 平均延迟(ms)或None
    """
    try:
        # ping一个可靠的服务器（如Google DNS）
        result = subprocess.run(["ping", "-c", "3", "8.8.8.8"], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            # 解析ping结果，提取平均延迟
            output = result.stdout
            match = re.search(r"min/avg/max/.+?/(\d+\.\d+)", output)
            if match:
                return float(match.group(1))
                
        return None
        
    except Exception as e:
        logger.error(f"网络质量测试出错: {e}")
        return None

def send_strength_to_server(strength, network_type="unknown"):
    """发送网络强度到服务器"""
    try:
        payload = {
            "strength": strength,
            "network_type": network_type,
            "timestamp": datetime.now().isoformat()
        }
        response = requests.post(SERVER_URL, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(f"成功发送数据: {strength} dBm ({network_type})")
            return True
        else:
            logger.error(f"服务器返回错误: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"发送数据时出错: {e}")
        return False

def request_permissions():
    """请求必要的权限"""
    try:
        logger.info("请求存储权限...")
        subprocess.run(["termux-setup-storage"], timeout=10)
        
        logger.info("请求位置权限...")
        # 尝试获取位置信息（会触发权限请求）
        subprocess.run(["termux-location", "-p", "network"], timeout=10)
        
        logger.info("权限请求已完成，请检查手机通知并授予所需权限")
    except Exception as e:
        logger.error(f"请求权限时出错: {e}")

def main():
    """主循环"""
    logger.info("开始监测网络强度...")
    
    # 首次运行时请求权限
    request_permissions()
    
    success_count = 0
    fail_count = 0
    
    while True:
        # 获取网络信息
        network_info = get_network_info_termux()
        network_type = "unknown"
        strength = None
        
        if network_info:
            network_type = network_info.get('type', 'unknown')
            strength = parse_signal_strength(network_info)
        
        # 如果无法从蜂窝网络获取，尝试WiFi
        if strength is None:
            wifi_info = get_wifi_info()
            if wifi_info and 'rssi' in wifi_info:
                strength = wifi_info['rssi']
                network_type = "wifi"
        
        # 如果仍然无法获取，使用网络质量指标
        if strength is None:
            network_quality = get_network_quality()
            if network_quality is not None:
                strength = max(-100, min(-50, -50 - (network_quality / 10)))
                network_type = "estimated"
        
        # 如果所有方法都失败，使用模拟数据
        if strength is None:
            strength = random.randint(-110, -60)
            network_type = "simulated"
            logger.warning("使用模拟数据进行测试")
        
        logger.info(f"当前网络强度: {strength} dBm ({network_type})")
        
        # 发送数据到服务器
        if send_strength_to_server(strength, network_type):
            success_count += 1
        else:
            fail_count += 1
        
        # 每10秒检测一次
        time.sleep(10)
        
        # 每10次输出一次统计信息
        if (success_count + fail_count) % 10 == 0:
            total = success_count + fail_count
            success_rate = (success_count / total) * 100 if total > 0 else 0
            logger.info(f"统计: 成功 {success_count}/{total} 次 ({success_rate:.1f}%)")

if __name__ == "__main__":
    main()