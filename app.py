import gradio as gr
import datetime
import random
import json

# 菜谱数据库
RECIPES_DATABASE = {
    "早餐": [
        "牛奶燕麦粥 + 水煮蛋 + 水果",
        "全麦面包 + 煎蛋 + 牛奶",
        "小米粥 + 咸菜 + 馒头",
        "豆浆 + 油条 + 小菜",
        "酸奶 + 坚果 + 全麦饼干",
        "鸡蛋羹 + 白粥 + 咸菜",
        "牛奶 + 面包片 + 香蕉"
    ],
    "午餐": [
        "红烧肉 + 青菜 + 米饭",
        "宫保鸡丁 + 土豆丝 + 米饭",
        "鱼香肉丝 + 青椒 + 米饭",
        "麻婆豆腐 + 青菜 + 米饭",
        "糖醋里脊 + 胡萝卜 + 米饭",
        "蒜蓉西兰花 + 鸡胸肉 + 米饭",
        "番茄炒蛋 + 青菜 + 米饭"
    ],
    "晚餐": [
        "清蒸鱼 + 青菜 + 米饭",
        "红烧茄子 + 鸡胸肉 + 米饭",
        "蒜蓉菠菜 + 鸡蛋 + 米饭",
        "青椒土豆丝 + 瘦肉 + 米饭",
        "番茄蛋汤 + 青菜 + 米饭",
        "蒸蛋羹 + 青菜 + 米饭",
        "豆腐汤 + 青菜 + 米饭"
    ],
    "加餐": [
        "苹果",
        "香蕉",
        "橙子",
        "酸奶",
        "坚果",
        "全麦饼干",
        "牛奶"
    ]
}

def generate_weekly_meal_plan(start_date=None):
    """生成一周的餐饮规划
    
    Args:
        start_date: 开始日期，默认为当前日期
        
    Returns:
        包含一周餐饮规划的字典
    """
    if start_date is None:
        start_date = datetime.datetime.now()
    elif isinstance(start_date, str):
        if "-" in start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        elif "年" in start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y年%m月%d日")
    
    # 获取一周的日期
    week_dates = []
    for i in range(7):
        current_date = start_date + datetime.timedelta(days=i)
        week_dates.append(current_date)
    
    # 生成一周的餐饮规划
    meal_plan = {}
    
    for i, date in enumerate(week_dates):
        date_str = date.strftime("%Y年%m月%d日")
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]
        
        # 为每天随机选择不同的菜谱
        daily_meals = {
            "早餐": random.choice(RECIPES_DATABASE["早餐"]),
            "午餐": random.choice(RECIPES_DATABASE["午餐"]),
            "晚餐": random.choice(RECIPES_DATABASE["晚餐"]),
            "加餐": random.choice(RECIPES_DATABASE["加餐"])
        }
        
        meal_plan[f"{weekday}({date_str})"] = daily_meals
    
    return meal_plan

def format_meal_plan(meal_plan):
    """格式化餐饮规划为可读的字符串
    
    Args:
        meal_plan: 餐饮规划字典
        
    Returns:
        格式化的字符串
    """
    result = "🍽️ 七日餐饮规划 🍽️\n"
    result += "=" * 50 + "\n\n"
    
    for day, meals in meal_plan.items():
        result += f"📅 {day}\n"
        result += "-" * 30 + "\n"
        for meal_type, meal in meals.items():
            result += f"🌅 {meal_type}: {meal}\n"
        result += "\n"
    
    return result

def meal_planner(start_date=""):
    """生成七日餐饮规划
    
    Args:
        start_date: 开始日期，接受datetime对象或字符串格式。默认为当前日期
        
    Returns:
        格式化的七日餐饮规划字符串
    """
    if start_date == "":
        start_date = None
    elif "-" in start_date:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    elif "年" in start_date:
        start_date = datetime.datetime.strptime(start_date, "%Y年%m月%d日")
    
    # 生成餐饮规划
    meal_plan = generate_weekly_meal_plan(start_date)
    
    # 格式化输出
    result = format_meal_plan(meal_plan)
    
    return result

# 创建Gradio界面
demo = gr.Interface(
    fn=meal_planner,
    inputs=[
        gr.Textbox(
            label="开始日期 (可选)",
            placeholder="格式: YYYY-MM-DD 或 YYYY年MM月DD日，留空使用当前日期",
            value=""
        )
    ],
    outputs=gr.Textbox(
        label="七日餐饮规划",
        lines=20,
        interactive=False
    ),
    title="🍽️ 七日餐饮规划助手 🍽️",
    description="为您生成一周的营养均衡餐饮规划，包含早餐、午餐、晚餐和加餐。",
    examples=[
        ["2024-01-15"],
        ["2024年01月15日"],
        [""]
    ]
)

# 启动应用，支持MCP
demo.launch(mcp_server=True, server_port=8000)