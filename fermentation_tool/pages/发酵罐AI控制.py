import streamlit as st
import time
import json
from pymodbus.client import ModbusTcpClient

# --------------------------
# 页面配置
# --------------------------
st.set_page_config(page_title="Modbus 智能助手", layout="wide")
st.title("🤖 发酵罐 Modbus 智能监控机器人")

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是你的Modbus助手\n我可以：\n✅ 读取pH/温度/溶氧\n✅ 修改PLC参数\n✅ 自动生成Python脚本\n✅ 实时监控报警\n请告诉我你的指令~"}
    ]

# PLC 全局配置
if "plc_config" not in st.session_state:
    st.session_state.plc_config = {
        "ip": "192.168.3.253",
        "port": 502,
        "ph_addr": 102,
        "temp_addr": 100,
        "do_addr": 104
    }

# --------------------------
# Modbus 工具函数
# --------------------------
def connect_plc(ip, port):
    try:
        client = ModbusTcpClient(ip, port)
        client.connect()
        return client
    except:
        return None

def read_reg(client, addr):
    try:
        res = client.read_holding_registers(addr, 1)
        if not res.isError():
            return round(res.registers[0] / 10.0, 2)
    except:
        return "ERROR"
    return "ERROR"

def write_reg(client, addr, value):
    try:
        client.write_register(addr, int(value * 10))
        return True
    except:
        return False

# --------------------------
# AI 指令解析
# --------------------------
def parse_command(msg):
    msg = msg.lower()
    c = st.session_state.plc_config
    
    # 读取数据
    if "读" in msg and ("ph" in msg or "ph值" in msg):
        return {"type":"read", "target":"ph"}
    elif "读" in msg and "温度" in msg:
        return {"type":"read", "target":"temp"}
    elif "读" in msg and "溶氧" in msg:
        return {"type":"read", "target":"do"}
    elif "全部" in msg or "所有" in msg:
        return {"type":"read_all"}
    
    # 修改参数
    elif "改" in msg and "ph" in msg:
        return {"type":"write", "target":"ph"}
    elif "改" in msg and "温度" in msg:
        return {"type":"write", "target":"temp"}
    
    # 生成脚本
    elif "脚本" in msg or "代码" in msg:
        return {"type":"gen_script"}
    
    # 设置PLC
    elif "ip" in msg or "plc" in msg:
        return {"type":"set_plc"}
    
    else:
        return {"type":"unknown"}

# --------------------------
# 生成 Python 脚本
# --------------------------
def generate_script():
    c = st.session_state.plc_config
    script = f'''
# 自动生成 Modbus 监控脚本
from pymodbus.client import ModbusTcpClient
import time

# PLC 配置
IP = "{c['ip']}"
PORT = {c['port']}
PH_ADDR = {c['ph_addr']}
TEMP_ADDR = {c['temp_addr']}
DO_ADDR = {c['do_addr']}

client = ModbusTcpClient(IP, PORT)
client.connect()

print("开始读取发酵罐数据...")
while True:
    ph = read_reg(client, PH_ADDR)
    temp = read_reg(client, TEMP_ADDR)
    do = read_reg(client, DO_ADDR)
    print(f"pH: {{ph}}  温度: {{temp}}  溶氧: {{do}}")
    time.sleep(1)
'''
    return script

# --------------------------
# 聊天界面
# --------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("输入指令：读pH/读温度/改参数/生成脚本/设置PLC")

if prompt:
    # 显示用户消息
    st.session_state.messages.append({"role":"user", "content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 解析指令
    cmd = parse_command(prompt)
    client = connect_plc(st.session_state.plc_config["ip"], 502)
    c = st.session_state.plc_config
    reply = ""

    # 执行动作
    if cmd["type"] == "read":
        if cmd["target"] == "ph":
            val = read_reg(client, c["ph_addr"])
            reply = f"✅ 当前pH值：**{val}**"
        elif cmd["target"] == "temp":
            val = read_reg(client, c["temp_addr"])
            reply = f"✅ 当前温度：**{val} ℃**"
        elif cmd["target"] == "do":
            val = read_reg(client, c["do_addr"])
            reply = f"✅ 当前溶氧：**{val} %**"

    elif cmd["type"] == "read_all":
        ph = read_reg(client, c["ph_addr"])
        temp = read_reg(client, c["temp_addr"])
        do = read_reg(client, c["do_addr"])
        reply = f"""📊 实时发酵数据：
pH：**{ph}**
温度：**{temp} ℃**
溶氧：**{do} %**"""

    elif cmd["type"] == "gen_script":
        script = generate_script()
        reply = f"✅ 已生成Python脚本：\n```python\n{script}\n```"

    elif cmd["type"] == "set_plc":
        reply = f"当前PLC配置：\nIP：{c['ip']}\npH地址：{c['ph_addr']}\n温度地址：{c['temp_addr']}"

    else:
        reply = "我可以帮你：\n✅ 读pH/温度/溶氧\n✅ 读取全部数据\n✅ 生成Python脚本\n✅ 设置PLC地址"

    # 回复
    st.session_state.messages.append({"role":"assistant", "content":reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

