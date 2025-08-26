from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import threading
import time
import json
import os

app = Flask(__name__)

# 存储网络强度数据
network_data = {
    'strength': 0,
    'network_type': 'unknown',
    'last_update': None,
    'history': [],
    'stats': {
        'max_strength': -60,  # 初始值
        'min_strength': -120, # 初始值
        'avg_strength': 0,
        'update_count': 0
    }
}

# 数据持久化
DATA_FILE = "network_data.json"

def load_data():
    """加载持久化数据"""
    global network_data
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                saved_data = json.load(f)
                # 只恢复需要持久化的数据
                network_data['history'] = saved_data.get('history', [])
                network_data['stats'] = saved_data.get('stats', network_data['stats'])
    except Exception as e:
        print(f"加载数据失败: {e}")

def save_data():
    """保存数据到文件"""
    try:
        data_to_save = {
            'history': network_data['history'],
            'stats': network_data['stats']
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(data_to_save, f)
    except Exception as e:
        print(f"保存数据失败: {e}")

# 启动时加载数据
load_data()

@app.route('/')
def index():
    return render_template('index.html', 
                         strength=network_data['strength'],
                         network_type=network_data['network_type'],
                         last_update=network_data['last_update'],
                         stats=network_data['stats'])

@app.route('/update', methods=['POST'])
def update_strength():
    try:
        data = request.get_json()
        strength = int(data.get('strength', 0))
        network_type = data.get('network_type', 'unknown')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # 更新数据
        network_data['strength'] = strength
        network_data['network_type'] = network_type
        network_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 更新统计信息
        network_data['stats']['update_count'] += 1
        network_data['stats']['max_strength'] = max(
            network_data['stats'].get('max_strength', -60), strength)
        network_data['stats']['min_strength'] = min(
            network_data['stats'].get('min_strength', -120), strength)
        
        # 计算平均强度
        total_updates = network_data['stats']['update_count']
        if total_updates == 1:
            network_data['stats']['avg_strength'] = strength
        else:
            prev_avg = network_data['stats']['avg_strength']
            network_data['stats']['avg_strength'] = (
                (prev_avg * (total_updates - 1) + strength) / total_updates
            )
        
        # 添加到历史记录（保留最近200条）
        network_data['history'].append({
            'time': network_data['last_update'],
            'strength': strength,
            'network_type': network_type,
            'timestamp': timestamp
        })
        if len(network_data['history']) > 200:
            network_data['history'].pop(0)
        
        # 保存数据
        save_data()
            
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/data')
def get_data():
    return jsonify(network_data)

@app.route('/stats')
def get_stats():
    """获取统计信息"""
    return jsonify(network_data['stats'])

@app.route('/history/<int:count>')
def get_history(count):
    """获取最近的历史记录"""
    if count <= 0 or count > 200:
        count = 50
    recent_history = network_data['history'][-count:] if network_data['history'] else []
    return jsonify(recent_history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)