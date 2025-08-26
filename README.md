📶 手机网络强度监测系统
一个用于实时监测手机网络信号强度并通过网页可视化展示的完整解决方案。该系统由手机端数据采集模块和服务器端数据展示模块组成，支持多种网络类型和信号强度获取方式。

# ✨ 功能特性

<div align="center">

功能	描述
📱 多网络支持	实时获取蜂窝网络(2G/3G/4G/5G)和WiFi信号强度

🌐 跨平台服务	服务器端支持Windows、macOS和Linux系统

📊 数据可视化	通过网页实时显示信号强度和变化趋势图表

🔔 智能识别	自动识别网络类型和信号质量等级

📈 历史记录	保存和展示历史数据，支持数据持久化

⚡ 实时更新	数据每10秒自动更新，网页每5秒刷新

📋 统计信息	显示最大、最小和平均信号强度等统计指标

🔧 容错机制	多种信号获取方法，支持优雅降级

</div>

# 📦 安装与部署

前置要求

🐍 Python 3.6 或更高版本

📱 Android 设备（用于移动数据采集）

🌐 网络连接（手机和服务器需在同一网络或可相互访问）

# 服务器端部署

克隆项目仓库：

bash

git clone https://github.com/shuoYun114/network-strength-monitor.git

cd network-strength-monitor

安装Python依赖：

bash

pip install -r requirements.txt

启动服务器：

bash

python server/app.py

打开浏览器访问 http://localhost:5000 查看监控界面

可选配置：修改服务器监听地址和端口（编辑 server/app.py）：

python

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)  # 允许远程访问

# 手机端设置

在Android设备上安装所需应用：

Termux (F-Droid/GitHub版本)

Termux:API (F-Droid/GitHub版本)

在Termux中执行以下命令安装依赖：

bash

pkg update && pkg upgrade

pkg install python termux-api

pip install requests

将手机端脚本传输到手机：

bash

# 通过SCP或ADB将mobile_client.py传输到手机

scp mobile/mobile_client.py user@手机IP:/path/to/script/

# 修改脚本中的服务器地址：

编辑mobile_client.py，将SERVER_URL改为您的服务器IP

SERVER_URL = "http://192.168.1.100:5000/update"  # 示例IP，请修改

运行数据采集脚本：

bash

python mobile_client.py

授予Termux必要权限：

首次运行时脚本会提示权限请求

或在Android设置中手动为Termux授予位置权限

# ⚙️ 配置说明

服务器配置选项

服务器端支持以下配置选项（通过修改 server/app.py）：

端口设置：默认使用5000端口

数据持久化：自动保存到JSON文件，重启后恢复历史数据

历史记录长度：默认保存最近200条记录

远程访问：设置 host='0.0.0.0' 允许远程连接

手机端配置选项

手机端支持以下配置选项（通过修改 mobile/mobile_client.py）：

数据发送间隔：默认10秒采集一次数据

服务器地址：需修改为实际服务器IP地址

信号获取方法：支持多种信号获取方式，自动选择最佳方法

超时设置：网络请求超时时间可调整

# 🚀 使用方法
启动服务器：在服务器上运行 python server/app.py

启动数据采集：在手机上运行 python mobile_client.py，随后即可将Termux退至后台（因为放在前台数据会不精确）

查看监控界面：在浏览器中打开 http://服务器IP:5000

监控信号强度：网页将实时显示信号强度图表和统计信息

#信号强度参考值

<div align="center">

信号强度(dBm)	信号质量	使用体验

≥ -70	优秀	流畅通话，高速上网

-70 到 -80	良好	稳定通话，良好网速

-80 到 -90	一般	通话可能中断，网速一般

-90 到 -100	较差	通话困难，网速慢

≤ -100	极差	基本无法使用

</div>

# 🔧 故障排除

常见问题及解决方案
问题	解决方案

无法获取网络信号数据	确保已安装Termux:API应用，检查是否授予了位置权限，尝试重启Termux应用

手机端无法连接到服务器	确认服务器IP地址正确，检查防火墙设置，确保5000端口开放，验证手机和服务器在同一网络

网页无法显示或加载缓慢	检查网络连接，确保设备可以访问互联网（需要加载Chart.js）

Termux命令执行超时	尝试增加超时时间（修改mobile_client.py中的timeout参数），检查Termux:API应用是否正常运行

# 获取帮助

如果您遇到其他问题，可以通过以下方式获取帮助：

提交 Issue

发送邮件至：syhx@syhx1.top,并附上错误信息

# 🤝 参与贡献
我们欢迎任何形式的贡献！以下是参与项目的方式：

🐛 报告问题：使用 Issue跟踪器 报告错误或提出建议

💻 功能开发：fork项目并提交Pull Request

📚 文档改进：帮助改进文档或翻译

🧪 测试反馈：测试系统并提供反馈

# 开发指南
Fork本项目

创建特性分支：git checkout -b feature/AmazingFeature

提交更改：git commit -m 'Add some AmazingFeature'

推送分支：git push origin feature/AmazingFeature

提交Pull Request

请确保您的代码遵循PEP 8规范，并添加适当的注释和测试。


# 🙏 致谢
Termux - 提供Android上的Linux环境

Flask - 轻量级Web框架

Chart.js - 优雅的JavaScript图表库

所有为本项目贡献代码和提出建议的开发者

# 📞 联系方式
项目维护者：烁云辉霞

邮箱：syhx@syhx1.top

项目链接：https://github.com/shuoYun114/network-strength-monitor