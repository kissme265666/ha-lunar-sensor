# HA Lunar Sensor

Home Assistant 自定义集成，提供农历日期、农历节日、二十四节气三个传感器。

## 安装

### 通过 HACS

1. HACS → 右上角 ⋮ → **自定义仓库**
2. 仓库: `https://github.com/kissme265666/ha-lunar-sensor`
3. 类型: **集成**
4. 添加后搜索 `农历传感器` 安装
5. 重启 Home Assistant

### 手动安装

将 `custom_components/lunar_sensor` 复制到 `config/custom_components/`，重启 HA。

## 配置

集成支持通过 UI 配置，无需 YAML：

1. 前往 **设置 → 设备与服务 → 添加集成**
2. 搜索 **农历传感器**
3. 点击提交即可完成配置

> 无需填写任何配置项，直接提交即可。

## 传感器

| 实体                    | 说明       | 示例     |
| ----------------------- | ---------- | -------- |
| `sensor.lunar_date`     | 农历日期   | 四月廿五 |
| `sensor.lunar_festival` | 农历节日   | 端午     |
| `sensor.solar_term`     | 二十四节气 | 芒种     |

节日自动去掉末尾"节"字保持两字（如"端午节"→"端午"），两字节日如"春节"保持不变。

## 依赖

- [lunar-python](https://pypi.org/project/lunar-python/)
