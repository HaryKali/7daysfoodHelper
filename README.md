---
# 7-Day Meal Planning Assistant

domain:
  # Domain: cv/nlp/audio/multi-modal/AutoML
# - cv

tags:
- meal-planning
- nutrition
- weekly-plan

datasets:
  evaluation:
  # - iic/ICDAR13_HCTR_Dataset
  test:
  # - iic/MTWI
  train:
  # - iic/SIBR

models:
# - iic/ofa_ocr-recognition_general_base_zh

## Startup File
# deployspec:
#   entry_file: app.py
license: Apache License 2.0
---

#### Clone with HTTP
```bash
git clone https://www.modelscope.cn/studios/minmin1023/luner_info1.git
```

## Project Features
This is a Gradio-based 7-day meal planning assistant with the following features:

### 🍽️ Core Features
- **7-Day Meal Planning**: Generates a nutritionally balanced weekly meal plan for users.
- **Diverse Menus**: Includes a rich selection for breakfast, lunch, dinner, and snacks.
- **Intelligent Randomization**: Provides different menu combinations every day to avoid repetition.
- **Flexible Date Setting**: Supports specifying a start date or using the current date.

### 🛠️ Technical Highlights
- **MCP Support**: Fully compatible with Model Context Protocol.
- **Gradio Interface**: Simple and user-friendly web interface.
- **Chinese Optimization**: Interface and menus are specially designed for Chinese users.

### 📋 Menu Types
- **Breakfast**: Nutritious breakfast options.
- **Lunch**: Balanced main course combinations.
- **Dinner**: Healthy dinner selections.
- **Snacks**: Healthy snacks such as fruits and nuts.

### 🚀 Usage
1. Run the application: `python app.py`
2. Enter the start date in the web interface (optional)
3. The system will automatically generate a 7-day meal plan
4. Supports multiple date formats: YYYY-MM-DD or YYYY年MM月DD
