#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动遍历HowToCook/dishes下的菜品，按早餐、午餐、晚餐、加餐分类，生成RECIPES_DATABASE并保存为recipes_database.py和recipes_database.json。
每道菜在JSON中包含做法链接。
"""
import os
import json
import urllib.parse

GITHUB_BASE = "https://github.com/Anduin2017/HowToCook/blob/master/dishes"

def get_dish_objs_from_dir(dir_path, category_dir):
    dishes = []
    if not os.path.exists(dir_path):
        return dishes
    for item in os.listdir(dir_path):
        if item.endswith('.md'):
            name = item[:-3]
            url = f"{GITHUB_BASE}/{urllib.parse.quote(category_dir)}/{urllib.parse.quote(item)}"
            dishes.append({"name": name, "url": url})
        elif os.path.isdir(os.path.join(dir_path, item)):
            # 检查目录下是否有.md文件
            dir_path_full = os.path.join(dir_path, item)
            md_files = [f for f in os.listdir(dir_path_full) if f.endswith('.md')]
            if md_files:
                # 使用第一个.md文件
                md_file = md_files[0]
                name = item
                url = f"{GITHUB_BASE}/{urllib.parse.quote(category_dir)}/{urllib.parse.quote(item)}/{urllib.parse.quote(md_file)}"
                dishes.append({"name": name, "url": url})
            else:
                # 没有.md文件，使用目录名
                name = item
                url = f"{GITHUB_BASE}/{urllib.parse.quote(category_dir)}/{urllib.parse.quote(item)}"
                dishes.append({"name": name, "url": url})
    return dishes

def main():
    base = 'HowToCook/dishes'
    # 分类
    breakfast = get_dish_objs_from_dir(os.path.join(base, 'breakfast'), 'breakfast')
    meat = get_dish_objs_from_dir(os.path.join(base, 'meat_dish'), 'meat_dish')
    veg = get_dish_objs_from_dir(os.path.join(base, 'vegetable_dish'), 'vegetable_dish')
    soup = get_dish_objs_from_dir(os.path.join(base, 'soup'), 'soup')
    dessert = get_dish_objs_from_dir(os.path.join(base, 'dessert'), 'dessert')
    staple = get_dish_objs_from_dir(os.path.join(base, 'staple'), 'staple')
    aquatic = get_dish_objs_from_dir(os.path.join(base, 'aquatic'), 'aquatic')

    # 早餐
    breakfast_recipes = [{"name": f"{dish['name']} + 牛奶/豆浆/粥", "url": dish["url"]} for dish in breakfast]
    # 午餐
    lunch_recipes = [{"name": f"{dish['name']} + 青菜 + 米饭", "url": dish["url"]} for dish in meat[:20]]
    lunch_recipes += [{"name": f"{dish['name']} + 米饭", "url": dish["url"]} for dish in veg[:10]]
    lunch_recipes += [{"name": f"{dish['name']} + 米饭", "url": dish["url"]} for dish in aquatic[:5]]
    # 晚餐
    dinner_recipes = [{"name": f"{dish['name']} + 米饭", "url": dish["url"]} for dish in veg[10:25]]
    dinner_recipes += [{"name": f"{dish['name']} + 米饭", "url": dish["url"]} for dish in meat[20:35]]
    dinner_recipes += [{"name": f"{dish['name']} + 米饭", "url": dish["url"]} for dish in soup[:10]]
    # 加餐
    snack_recipes = [{"name": dish['name'], "url": dish["url"]} for dish in dessert[:10]]
    snack_recipes += [{"name": fruit, "url": ""} for fruit in ['苹果', '香蕉', '橙子', '葡萄', '草莓', '蓝莓', '猕猴桃', '柚子', '梨', '桃子']]

    RECIPES_DATABASE = {
        '早餐': breakfast_recipes,
        '午餐': lunch_recipes,
        '晚餐': dinner_recipes,
        '加餐': snack_recipes
    }

    # 保存为py
    with open('recipes_database.py', 'w', encoding='utf-8') as f:
        f.write('# 自动生成的菜谱数据库\n')
        f.write('RECIPES_DATABASE = ')
        json.dump(RECIPES_DATABASE, f, ensure_ascii=False, indent=2)
    # 保存为json
    with open('recipes_database.json', 'w', encoding='utf-8') as f:
        json.dump(RECIPES_DATABASE, f, ensure_ascii=False, indent=2)
    print('已生成 recipes_database.py 和 recipes_database.json')

if __name__ == '__main__':
    main()