import gradio as gr
import datetime
import random
import json
import os
import requests
import re

# 尝试从recipes_database.py导入菜谱数据库
try:
    from recipes_database import RECIPES_DATABASE
    print("✅ 成功从 recipes_database.py 导入菜谱数据库")
except ImportError:
    print("⚠️ 未找到 recipes_database.py，使用默认菜谱数据库")
    # 默认菜谱数据库（作为备用）
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

def generate_weekly_meal_plan(start_date=None, health_goal="无目标", taste_preferences=None):
    """生成一周的餐饮规划，支持健康目标和口味偏好筛选"""
    if start_date is None:
        start_date = datetime.datetime.now()
    elif isinstance(start_date, str):
        if "-" in start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        elif "年" in start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y年%m月%d日")
    week_dates = [start_date + datetime.timedelta(days=i) for i in range(7)]
    meal_plan = {}
    if taste_preferences is None:
        taste_preferences = []
    # 口味偏好关键词映射
    taste_keywords = {
        "不要香菜": ["香菜"],
        "不吃乳制品": ["奶", "牛奶", "奶酪", "芝士", "黄油", "乳", "酸奶", "蛋糕", "蛋挞"],
        "不吃葱": ["葱"],
        "素食": ["鸡", "鸭", "鱼", "肉", "牛", "排骨", "猪", "虾", "蟹", "肝", "鸡翅", "鸡胸", "鸡腿", "鸡蛋", "牛肉", "猪肉", "羊肉", "鸭肉", "鱼肉", "排骨", "虾仁", "蟹肉", "肝脏", "兔", "兔肉"],
        "不吃辣": ["辣", "辣椒", "小米辣", "剁椒", "麻辣", "香辣", "泡椒", "青椒", "红椒", "干辣椒"]
    }
    def filter_recipe(recipe, health_goal, taste_preferences, meal_type=None):
        name = recipe["name"] if isinstance(recipe, dict) else recipe
        # 健康目标过滤
        if health_goal == "减脂":
            if any(x in name for x in ["炸", "油炸", "甜品", "糖", "蛋糕", "奶茶", "甜汤"]):
                return False
        # 口味偏好过滤
        for pref in taste_preferences:
            if pref == "素食":
                # 素食：只要有荤菜关键词就排除
                if any(x in name for x in taste_keywords["素食"]):
                    return False
            else:
                if any(x in name for x in taste_keywords[pref]):
                    return False
        return True
    protein_keywords = ["鸡", "鸭", "鱼", "肉", "牛", "排骨", "猪", "蛋", "豆"]
    for i, date in enumerate(week_dates):
        date_str = date.strftime("%Y年%m月%d日")
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]
        daily_meals = {}
        meal_types = ["早餐", "午餐", "晚餐"] if health_goal == "减脂" else ["早餐", "午餐", "晚餐", "加餐"]
        for meal_type in meal_types:
            if meal_type in RECIPES_DATABASE:
                filtered = []
                for r in RECIPES_DATABASE[meal_type]:
                    # 针对早餐和不吃乳制品，做特殊处理
                    if meal_type == "早餐" and "不吃乳制品" in taste_preferences:
                        name = r["name"] if isinstance(r, dict) else r
                        parts = [p.strip() for p in name.split("+")]
                        non_dairy_parts = [p for p in parts if not any(x in p for x in taste_keywords["不吃乳制品"])]
                        if non_dairy_parts:
                            new_name = " + ".join(non_dairy_parts)
                            if filter_recipe({"name": new_name}, health_goal, [p for p in taste_preferences if p != "不吃乳制品"], meal_type):
                                if isinstance(r, dict):
                                    filtered.append({"name": new_name, "url": r.get("url", "")})
                                else:
                                    filtered.append(new_name)
                    else:
                        if filter_recipe(r, health_goal, taste_preferences, meal_type):
                            filtered.append(r)
                # 素食早餐无可选时，自动用加餐中的水果类补充
                if meal_type == "早餐" and "素食" in taste_preferences and not filtered:
                    fruit_keywords = ["苹果", "香蕉", "橙子", "葡萄", "草莓", "蓝莓", "猕猴桃", "柚子", "梨", "桃子"]
                    fruit_choices = []
                    for snack in RECIPES_DATABASE.get("加餐", []):
                        snack_name = snack["name"] if isinstance(snack, dict) else snack
                        if any(f in snack_name for f in fruit_keywords):
                            fruit_choices.append(snack)
                    if fruit_choices:
                        filtered.append(random.choice(fruit_choices))
                if health_goal == "增肌":
                    protein_rich = [r for r in filtered if any(k in (r["name"] if isinstance(r, dict) else r) for k in protein_keywords)]
                    if protein_rich:
                        choice = random.choice(protein_rich)
                    elif filtered:
                        choice = random.choice(filtered)
                    else:
                        daily_meals[meal_type] = {"name": "❌ 无可用菜品，请减少忌口选项", "url": ""}
                        continue
                else:
                    if filtered:
                        choice = random.choice(filtered)
                    else:
                        daily_meals[meal_type] = {"name": "❌ 无可用菜品，请减少忌口选项", "url": ""}
                        continue
                if isinstance(choice, dict):
                    daily_meals[meal_type] = {"name": choice["name"], "url": choice.get("url", "")}
                else:
                    daily_meals[meal_type] = {"name": choice, "url": ""}
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
    result += "═" * 60 + "\n\n"
    
    for day, meals in meal_plan.items():
        result += f"📅 {day}\n"
        result += "─" * 40 + "\n"
        
        # 定义餐点图标
        meal_icons = {
            "早餐": "🌅",
            "午餐": "🌞", 
            "晚餐": "🌙",
            "加餐": "🍎"
        }
        
        for meal_type, meal_info in meals.items():
            icon = meal_icons.get(meal_type, "🍽️")
            
            if isinstance(meal_info, dict):
                meal_name = meal_info["name"]
                meal_url = meal_info.get("url", "")
                
                result += f"{icon} {meal_type}: {meal_name}\n"
                if meal_url:
                    result += f"   🔗 做法: {meal_url}\n"
            else:
                # 兼容旧格式
                result += f"{icon} {meal_type}: {meal_info}\n"
        
        result += "\n" + "═" * 60 + "\n\n"
    
    return result

def meal_planner(start_date="", health_goal="无目标", taste_preferences=None):
    if start_date == "":
        start_date = None
    elif "-" in start_date:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    elif "年" in start_date:
        start_date = datetime.datetime.strptime(start_date, "%Y年%m月%d日")
    meal_plan = generate_weekly_meal_plan(start_date, health_goal, taste_preferences)
    result = format_meal_plan(meal_plan)
    return result

def get_recipe_content(url):
    """从GitHub获取菜品做法内容
    
    Args:
        url: GitHub链接
        
    Returns:
        菜品做法内容或错误信息
    """
    try:
        # 将GitHub链接转换为raw链接
        # 例如: https://github.com/Anduin2017/HowToCook/blob/master/dishes/breakfast/太阳蛋.md
        # 转换为: https://raw.githubusercontent.com/Anduin2017/HowToCook/master/dishes/breakfast/太阳蛋.md
        
        if "github.com" in url and "/blob/" in url:
            raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        else:
            raw_url = url
        
        print(f"正在获取: {raw_url}")  # 调试信息
        
        response = requests.get(raw_url, timeout=10)
        if response.status_code == 200:
            content = response.text
            return content
        else:
            return f"❌ 无法获取菜品做法，HTTP状态码: {response.status_code}\nURL: {raw_url}"
    except Exception as e:
        return f"❌ 获取菜品做法时出错: {str(e)}\nURL: {raw_url}"

def format_recipe_content(content, recipe_name):
    """格式化菜品做法内容
    
    Args:
        content: 原始Markdown内容
        recipe_name: 菜品名称
        
    Returns:
        格式化的做法内容
    """
    if not content or content.startswith("❌"):
        return content
    
    # 移除Markdown标记，保留文本内容
    lines = content.split('\n')
    formatted_lines = []
    
    for line in lines:
        # 移除Markdown标题标记
        line = re.sub(r'^#+\s*', '', line)
        # 移除Markdown链接标记
        line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
        # 移除Markdown粗体标记
        line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
        # 移除Markdown斜体标记
        line = re.sub(r'\*([^*]+)\*', r'\1', line)
        # 移除Markdown代码标记
        line = re.sub(r'`([^`]+)`', r'\1', line)
        
        if line.strip():
            formatted_lines.append(line)
    
    result = f"🍽️ {recipe_name} 详细做法\n"
    result += "═" * 50 + "\n\n"
    result += '\n'.join(formatted_lines)
    
    return result

def search_recipe(recipe_name):
    """搜索菜品做法
    
    Args:
        recipe_name: 菜品名称
        
    Returns:
        菜品做法信息或错误提示
    """
    if not recipe_name or recipe_name.strip() == "":
        return "请输入要搜索的菜品名称"
    
    recipe_name = recipe_name.strip()
    
    # 在所有菜谱中搜索
    found_recipes = []
    
    for meal_type, recipes in RECIPES_DATABASE.items():
        for recipe in recipes:
            if isinstance(recipe, dict):
                recipe_display_name = recipe["name"]
                # 提取原始菜品名（去掉搭配部分）
                original_name = recipe_display_name.split(" + ")[0]
                if recipe_name.lower() in original_name.lower() or recipe_name.lower() in recipe_display_name.lower():
                    found_recipes.append({
                        "name": recipe_display_name,
                        "url": recipe.get("url", ""),
                        "category": meal_type
                    })
            else:
                # 兼容旧格式
                if recipe_name.lower() in recipe.lower():
                    found_recipes.append({
                        "name": recipe,
                        "url": "",
                        "category": meal_type
                    })
    
    if not found_recipes:
        return f"❌ 抱歉，没有找到包含 '{recipe_name}' 的菜品\n\n💡 提示：\n- 请检查菜品名称是否正确\n- 可以尝试搜索菜品的关键词\n- 例如：搜索 '鸡蛋' 可以找到 '太阳蛋'、'蒸水蛋' 等"
    
    # 如果只找到一个菜品，直接显示详细做法
    if len(found_recipes) == 1:
        recipe = found_recipes[0]
        if recipe['url']:
            content = get_recipe_content(recipe['url'])
            return format_recipe_content(content, recipe['name'])
        else:
            return f"🍽️ {recipe['name']}\n📂 分类: {recipe['category']}\n\n❌ 该菜品暂无详细做法链接"
    
    # 如果找到多个菜品，显示列表
    result = f"🔍 找到 {len(found_recipes)} 个相关菜品：\n"
    result += "═" * 50 + "\n\n"
    result += "请选择其中一个菜品查看详细做法：\n\n"
    
    for i, recipe in enumerate(found_recipes, 1):
        result += f"{i}. 🍽️ {recipe['name']}\n"
        result += f"   📂 分类: {recipe['category']}\n"
        if recipe['url']:
            result += f"   🔗 做法链接: {recipe['url']}\n"
        result += "\n"
    
    result += "💡 提示：输入完整的菜品名称可以查看详细做法"
    
    return result

def exact_search_recipe(recipe_name):
    """精确搜索菜品做法
    
    Args:
        recipe_name: 完整的菜品名称
        
    Returns:
        菜品详细做法
    """
    if not recipe_name or recipe_name.strip() == "":
        return "请输入要搜索的菜品名称"
    
    recipe_name = recipe_name.strip()
    
    # 在所有菜谱中精确搜索
    for meal_type, recipes in RECIPES_DATABASE.items():
        for recipe in recipes:
            if isinstance(recipe, dict):
                recipe_display_name = recipe["name"]
                # 提取原始菜品名（去掉搭配部分）
                original_name = recipe_display_name.split(" + ")[0]
                if recipe_name.lower() == original_name.lower():
                    if recipe.get("url"):
                        content = get_recipe_content(recipe["url"])
                        return format_recipe_content(content, recipe_display_name)
                    else:
                        return f"🍽️ {recipe_display_name}\n📂 分类: {meal_type}\n\n❌ 该菜品暂无详细做法链接"
            else:
                # 兼容旧格式
                if recipe_name.lower() == recipe.lower():
                    return f"🍽️ {recipe}\n📂 分类: {meal_type}\n\n❌ 该菜品暂无详细做法链接"
    
    return f"❌ 抱歉，没有找到名为 '{recipe_name}' 的菜品\n\n💡 提示：\n- 请确保输入的是完整的菜品名称\n- 可以尝试搜索关键词来查看相关菜品"

def generate_spring_festival_menu(people_count):
    """生成春节菜单
    
    Args:
        people_count: 人数
        
    Returns:
        春节菜单
    """
    if people_count <= 0:
        return "请输入有效的人数"
    
    # 春节必备菜品（鸡鸭鱼）
    essential_dishes = [
        "宫保鸡丁",
        "啤酒鸭", 
        "清蒸鳜鱼"
    ]
    
    # 肉菜菜品库
    meat_dishes = [
        "红烧肉",
        "糖醋里脊",
        "回锅肉",
        "梅菜扣肉",
        "孜然牛肉",
        "土豆炖排骨",
        "商芝肉",
        "咕噜肉",
        "咖喱肥牛",
        "姜炒鸡",
        "姜葱捞鸡",
        "乡村啤酒鸭",
        "农家一碗香",
        "冬瓜酿肉",
        "凉拌鸡丝",
        "口水鸡",
        "可乐鸡翅",
        "台式卤肉饭"
    ]
    
    # 素菜菜品库
    vegetable_dishes = [
        "蒜蓉西兰花",
        "凉拌黄瓜",
        "上汤娃娃菜",
        "凉拌木耳",
        "凉拌豆腐",
        "凉拌金针菇",
        "凉拌油麦菜",
        "凉拌莴笋",
        "西红柿炒鸡蛋",
        "蒜蓉空心菜",
        "蚝油生菜",
        "清炒花菜",
        "地三鲜",
        "干锅花菜",
        "红烧茄子"
    ]
    
    # 主食
    staple_foods = [
        "米饭",
        "馒头",
        "花卷",
        "包子"
    ]
    
    # 青菜
    green_vegetables = [
        "清炒小白菜",
        "蒜蓉菠菜",
        "蚝油生菜",
        "清炒油麦菜",
        "蒜蓉空心菜"
    ]
    
    # 计算需要的菜品数量（n+1道菜）
    total_dishes_needed = people_count + 1
    
    # 计算最少需要的肉菜数量（n/2 + 2）
    min_meat_dishes_needed = max(3, int(people_count / 2) + 2)  # 至少3道（鸡鸭鱼）
    
    # 确保包含鸡鸭鱼
    selected_dishes = essential_dishes.copy()
    
    # 计算还需要多少道肉菜
    additional_meat_needed = min_meat_dishes_needed - len(essential_dishes)
    
    # 从肉菜库中随机选择额外的肉菜
    if additional_meat_needed > 0:
        available_meat_dishes = [dish for dish in meat_dishes if dish not in selected_dishes]
        if available_meat_dishes:
            additional_meat = random.sample(available_meat_dishes, min(additional_meat_needed, len(available_meat_dishes)))
            selected_dishes.extend(additional_meat)
    
    # 计算还需要多少道素菜
    remaining_dishes_needed = total_dishes_needed - len(selected_dishes)
    if remaining_dishes_needed > 0:
        additional_vegetables = random.sample(vegetable_dishes, min(remaining_dishes_needed, len(vegetable_dishes)))
        selected_dishes.extend(additional_vegetables)
    
    # 检查是否需要添加主食和青菜
    has_staple = any(keyword in dish for dish in selected_dishes for keyword in ["饭", "馒头", "花卷", "包子", "水饺", "元宵"])
    has_green_veg = any(keyword in dish for dish in selected_dishes for keyword in ["菜", "菠菜", "生菜", "油麦菜", "空心菜"])
    
    # 如果没有主食，添加一个主食
    if not has_staple:
        staple = random.choice(staple_foods)
        selected_dishes.append(staple)
    
    # 如果没有青菜，添加一个青菜
    if not has_green_veg:
        green_veg = random.choice(green_vegetables)
        selected_dishes.append(green_veg)
    
    # 统计菜品类型
    meat_count = sum(1 for dish in selected_dishes if any(keyword in dish for keyword in ["鸡", "鸭", "鱼", "肉", "牛", "排骨", "猪"]))
    vegetable_count = len(selected_dishes) - meat_count
    
    # 格式化输出
    result = f"🏮 春节菜单 🏮 ({people_count}人)\n"
    result += "═" * 60 + "\n\n"
    result += f"📊 菜单信息：\n"
    result += f"   👥 人数：{people_count}人\n"
    result += "🍽️ 菜品清单：\n"
    result += "─" * 40 + "\n"
    
    for i, dish in enumerate(selected_dishes, 1):
        # 添加emoji标识
        if "鸡" in dish:
            emoji = "🐔"
        elif "鸭" in dish:
            emoji = "🦆"
        elif "鱼" in dish:
            emoji = "🐟"
        elif any(keyword in dish for keyword in ["肉", "牛", "排骨", "猪"]):
            emoji = "🥩"
        elif "菜" in dish or "花" in dish or "菇" in dish or "蛋" in dish:
            emoji = "🥬"
        else:
            emoji = "🍽️"
        
        result += f"{i:2d}. {emoji} {dish}\n"
    
    result += "\n" + "═" * 60 + "\n"
    result += "💡 春节菜单特点：\n"
    result += "   • 必备三样：鸡（大吉大利）、鸭（压岁）、鱼（年年有余）\n"
    result += "   • 荤素搭配：营养均衡\n"
    result += "   • 寓意吉祥：每道菜都有美好寓意\n"
    
    return result

def generate_lantern_festival_menu(people_count, region):
    """生成元宵节菜单，region可为'south', 'north', ''"""
    if people_count <= 0:
        return "请输入有效的人数"
    # 如果region为空或为直接推荐，推荐一组美食菜单
    if not region or region == "直接推荐":
        # 推荐美食菜单（不带地区特色）
        recommended_dishes = [
            "红烧肉", "宫保鸡丁", "清蒸鱼", "蒜蓉西兰花", "凉拌黄瓜", "上汤娃娃菜", "地三鲜", "干锅花菜", "红烧茄子", "八宝粥", "银耳莲子羹", "元宵", "水饺"
        ]
        selected_dishes = random.sample(recommended_dishes, min(people_count+1, len(recommended_dishes)))
        result = f"🏮 元宵节美食推荐 🏮 ({people_count}人)\n"
        result += "═" * 60 + "\n\n"
        result += f"📊 菜单信息：\n"
        result += f"   👥 人数：{people_count}人\n"
        result += "🍽️ 菜品清单：\n"
        result += "─" * 40 + "\n"
        for i, dish in enumerate(selected_dishes, 1):
            emoji = "🍽️"
            if "鸡" in dish:
                emoji = "🐔"
            elif "鸭" in dish:
                emoji = "🦆"
            elif "鱼" in dish:
                emoji = "🐟"
            elif "肉" in dish or "牛" in dish or "排骨" in dish or "猪" in dish:
                emoji = "🥩"
            elif "菜" in dish or "花" in dish or "菇" in dish or "蛋" in dish:
                emoji = "🥬"
            elif "粥" in dish or "羹" in dish or "汤" in dish:
                emoji = "🍡"
            elif "元宵" in dish:
                emoji = "🥣"
            elif "水饺" in dish:
                emoji = "🥟"
            result += f"{i:2d}. {emoji} {dish}\n"
        result += "\n" + "═" * 60 + "\n"
        result += "💡 元宵节菜单特点：\n"
        result += "   • 经典美食推荐，南北皆宜\n"
        result += "   • 团圆寓意：元宵/水饺象征团团圆圆\n"
        result += "   • 荤素搭配，营养均衡\n"
        result += "   • 节日氛围，适合家庭聚餐\n"
        return result
    # 推荐南方美食
    if region == "推荐南方美食":
        region = "south"
    elif region == "推荐北方美食":
        region = "north"
    # 根据地区确定必备菜品
    if region == "south":
        essential_dish = "元宵"
        essential_emoji = "🥣"
        region_name = "南方"
        region_desc = "南方特色：元宵（团团圆圆）"
        traditional_dishes = [
            "红烧肉",
            "糖醋里脊",
            "宫保鸡丁",
            "清蒸鱼",
            "蒜蓉西兰花",
            "凉拌黄瓜",
            "上汤娃娃菜",
            "凉拌木耳",
            "凉拌豆腐",
            "西红柿炒鸡蛋",
            "蒜蓉空心菜",
            "蚝油生菜",
            "清炒花菜",
            "地三鲜",
            "干锅花菜",
            "红烧茄子",
            "凉拌金针菇",
            "凉拌油麦菜",
            "凉拌莴笋"
        ]
        total_dishes_needed = people_count + 1
        selected_dishes = [essential_dish]
        remaining_dishes_needed = total_dishes_needed - 1
        if remaining_dishes_needed > 0:
            main_dishes = random.sample(traditional_dishes, min(remaining_dishes_needed, len(traditional_dishes)))
            selected_dishes.extend(main_dishes)
        # 检查是否需要添加主食和青菜
        has_staple = any(keyword in dish for dish in selected_dishes for keyword in ["饭", "馒头", "花卷", "包子", "元宵"])
        has_green_veg = any(keyword in dish for dish in selected_dishes for keyword in ["菜", "菠菜", "生菜", "油麦菜", "空心菜"])
        if not has_staple:
            staple_foods = ["米饭", "馒头", "花卷", "包子"]
            staple = random.choice(staple_foods)
            selected_dishes.append(staple)
        if not has_green_veg:
            green_vegetables = ["清炒小白菜", "蒜蓉菠菜", "蚝油生菜", "清炒油麦菜", "蒜蓉空心菜"]
            green_veg = random.choice(green_vegetables)
            selected_dishes.append(green_veg)
        result = f"🏮 元宵节菜单 🏮 (推荐南方美食，{people_count}人)\n"
        result += "═" * 60 + "\n\n"
        result += f"📊 菜单信息：\n"
        result += f"   🌍 地区：南方\n"
        result += f"   👥 人数：{people_count}人\n"
        result += "🍽️ 菜品清单：\n"
        result += "─" * 40 + "\n"
        for i, dish in enumerate(selected_dishes, 1):
            if essential_dish in dish:
                emoji = essential_emoji
            elif any(keyword in dish for keyword in ["肉", "鸡", "鱼", "牛", "排骨", "猪"]):
                emoji = "🥩"
            elif any(keyword in dish for keyword in ["菜", "花", "菇", "蛋", "豆", "瓜"]):
                emoji = "🥬"
            else:
                emoji = "🍽️"
            result += f"{i:2d}. {emoji} {dish}\n"
        result += "\n" + "═" * 60 + "\n"
        result += "💡 元宵节菜单特点：\n"
        result += "   • 南方特色：元宵为甜点，配以传统菜品\n"
        result += "   • 团圆寓意：元宵象征团团圆圆\n"
        result += "   • 荤素搭配，营养均衡\n"
        result += "   • 节日氛围，适合家庭聚餐\n"
        return result
    elif region == "north":
        # 北方水饺种类库
        dumpling_dishes = [
            "白菜猪肉水饺", "韭菜鸡蛋水饺", "三鲜水饺", "芹菜猪肉水饺", "胡萝卜牛肉水饺", "香菇鸡肉水饺", "虾仁水饺", "韭菜猪肉水饺", "白菜虾仁水饺", "芹菜牛肉水饺", "胡萝卜猪肉水饺", "香菇猪肉水饺", "韭菜虾仁水饺", "白菜鸡蛋水饺", "芹菜虾仁水饺"
        ]
        # 其他北方美食
        other_dishes = [
            "红烧肉", "宫保鸡丁", "清蒸鱼", "蒜蓉西兰花", "凉拌黄瓜", "上汤娃娃菜", "地三鲜", "干锅花菜", "红烧茄子", "元宵"
        ]
        dessert_dishes = [
            "八宝粥", "银耳莲子羹", "红豆沙", "绿豆汤", "冰糖雪梨", "红枣桂圆汤", "莲子百合汤", "杏仁茶"
        ]
        total_dishes_needed = people_count + 1
        # 饺子最多占一半（向上取整）
        max_dumplings = (total_dishes_needed - 1 + 1) // 2  # -1为甜点，+1向上取整
        dumpling_count = min(max_dumplings, len(dumpling_dishes))
        selected_dumplings = random.sample(dumpling_dishes, dumpling_count)
        # 甜点
        dessert = random.choice(dessert_dishes)
        # 剩余名额
        other_count = total_dishes_needed - dumpling_count - 1
        selected_others = random.sample(other_dishes, min(other_count, len(other_dishes)))
        selected_dishes = selected_dumplings + selected_others + [dessert]
        result = f"🏮 元宵节菜单 🏮 (推荐北方美食，{people_count}人)\n"
        result += "═" * 60 + "\n\n"
        result += f"📊 菜单信息：\n"
        result += f"   🌍 地区：北方\n"
        result += f"   👥 人数：{people_count}人\n"
        result += "🍽️ 菜品清单：\n"
        result += "─" * 40 + "\n"
        for i, dish in enumerate(selected_dishes, 1):
            emoji = "🍽️"
            if "水饺" in dish:
                emoji = "🥟"
            elif any(keyword in dish for keyword in ["粥", "羹", "茶", "汤", "沙"]):
                emoji = "🍡"
            else:
                emoji = "🍽️"
            result += f"{i:2d}. {emoji} {dish}\n"
        result += "\n" + "═" * 60 + "\n"
        result += "💡 元宵节菜单特点：\n"
        result += "   • 北方特色：水饺为主，搭配多样美食\n"
        result += "   • 团圆寓意：元宵/水饺象征团团圆圆\n"
        result += "   • 荤素搭配，营养均衡\n"
        result += "   • 节日氛围，适合家庭聚餐\n"
        return result

# 创建Gradio界面
with gr.Blocks(title="🍽️ 七日餐饮规划助手 🍽️") as demo:
    gr.Markdown("# 🍽️ 七日餐饮规划助手 🍽️")
    gr.Markdown("为您生成一周的营养均衡餐饮规划，包含早餐、午餐、晚餐和加餐。")
    
    with gr.Tabs():
        # 第一个标签页：七日餐饮规划
        with gr.TabItem("📅 七日餐饮规划"):
            with gr.Row():
                with gr.Column():
                    date_input = gr.Textbox(
                        label="开始日期 (可选)",
                        placeholder="格式: YYYY-MM-DD 或 YYYY年MM月DD日，留空使用当前日期",
                        value=""
                    )
                    # 新增饮食健康目标选项
                    health_goal_radio = gr.Radio(
                        label="饮食健康目标",
                        choices=["无目标", "增肌", "减脂"],
                        value="无目标",
                        info="选择后将自动调整一周餐饮规划"
                    )
                    taste_checkbox = gr.CheckboxGroup(
                        label="口味/忌口偏好（可多选）",
                        choices=["不要香菜", "不吃乳制品", "不吃葱", "不吃辣", "素食"],
                        value=[],
                        info="选择后将自动过滤不喜欢的食材"
                    )
                    generate_btn = gr.Button("🚀 生成餐饮规划", variant="primary")
                
                with gr.Column():
                    meal_plan_output = gr.Textbox(
                        label="七日餐饮规划",
                        lines=25,
                        interactive=False
                    )
            
            # 示例
            gr.Examples(
                examples=[
                    ["2024-01-15"],
                    ["2024年01月15日"],
                ],
                inputs=date_input
            )
        
        # 第二个标签页：菜品搜索
        with gr.TabItem("🔍 菜品搜索"):
            with gr.Row():
                with gr.Column():
                    search_input = gr.Textbox(
                        label="搜索菜品",
                        placeholder="输入菜品名称，如：宫保鸡丁、太阳蛋、红烧肉等",
                        value=""
                    )
                    with gr.Row():
                        search_btn = gr.Button("🔍 模糊搜索", variant="primary")
                        exact_search_btn = gr.Button("🎯 精确搜索", variant="secondary")
                
                with gr.Column():
                    search_output = gr.Textbox(
                        label="搜索结果",
                        lines=25,
                        interactive=False
                    )
            
            # 搜索示例
            gr.Examples(
                examples=[
                    ["宫保鸡丁"],
                    ["太阳蛋"],
                    ["红烧肉"],
                    ["鸡蛋"],
                    ["鸡"],
                ],
                inputs=search_input
            )
        
        # 第三个标签页：节庆菜单
        with gr.TabItem("🏮 节庆菜单"):
            with gr.Tabs():
                # 春节菜单子标签页
                with gr.TabItem("🏮 春节菜单"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### 🏮 春节菜单生成器")
                            gr.Markdown("根据人数自动生成春节菜单，确保包含鸡鸭鱼等传统菜品")
                            
                            people_count_input = gr.Number(
                                label="用餐人数",
                                value=4,
                                minimum=1,
                                maximum=20
                            )
                            spring_festival_btn = gr.Button("🏮 生成春节菜单", variant="primary")
                        
                        with gr.Column():
                            festival_output = gr.Textbox(
                                label="春节菜单",
                                lines=30,
                                interactive=False
                            )
                    
                    # 春节菜单示例
                    gr.Examples(
                        examples=[
                            [4],
                            [6],
                            [8],
                            [10],
                        ],
                        inputs=people_count_input
                    )
                
                # 元宵节菜单子标签页
                with gr.TabItem("🏮 元宵节菜单"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### 🏮 元宵节菜单生成器")
                            gr.Markdown("根据地区和人数生成元宵节菜单，南方必备元宵，北方必备水饺")
                            
                            lantern_people_count = gr.Number(
                                label="用餐人数",
                                value=4,
                                minimum=1,
                                maximum=20
                            )
                            # 修改地区选择选项
                            region_choice = gr.Radio(
                                label="选择地区",
                                choices=["推荐南方美食", "推荐北方美食", "直接推荐"],
                                value="直接推荐",
                                info="可选推荐南方美食、推荐北方美食，或直接推荐经典美食"
                            )
                            lantern_festival_btn = gr.Button("🏮 生成元宵节菜单", variant="primary")
                        
                        with gr.Column():
                            lantern_festival_output = gr.Textbox(
                                label="元宵节菜单",
                                lines=30,
                                interactive=False
                            )
                    
                    # 元宵节菜单示例
                    gr.Examples(
                        examples=[
                            [4, "南方"],
                            [6, "北方"],
                            [8, "南方"],
                            [10, "北方"],
                        ],
                        inputs=[lantern_people_count, region_choice]
                    )
    
    # 绑定事件
    generate_btn.click(
        fn=meal_planner,
        inputs=[date_input, health_goal_radio, taste_checkbox],
        outputs=meal_plan_output
    )
    
    search_btn.click(
        fn=search_recipe,
        inputs=search_input,
        outputs=search_output
    )
    
    # 回车键搜索
    search_input.submit(
        fn=search_recipe,
        inputs=search_input,
        outputs=search_output
    )
    
    # 绑定精确搜索事件
    exact_search_btn.click(
        fn=exact_search_recipe,
        inputs=search_input,
        outputs=search_output
    )
    
    # 绑定春节菜单事件
    spring_festival_btn.click(
        fn=generate_spring_festival_menu,
        inputs=people_count_input,
        outputs=festival_output
    )
    
    # 元宵节菜单处理函数
    def lantern_festival_handler(people_count, region):
        """处理元宵节菜单生成"""
        region_code = region
        return generate_lantern_festival_menu(people_count, region_code)
    
    # 绑定元宵节菜单事件
    lantern_festival_btn.click(
        fn=lantern_festival_handler,
        inputs=[lantern_people_count, region_choice],
        outputs=lantern_festival_output
    )

# 启动应用，支持MCP
demo.launch(mcp_server=True, server_port=8000)