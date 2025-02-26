

#目前不可用
class PID:
    
    """
参数：
kp  比例系数
ki  积分系数
kd  微分系数

integral   积分项，用于累计误差
prev_error 上一周期的误差，用于计算微分项

integral_limit 积分项限幅，用于避免积分项过大
output_limit   控制器输出的限幅，防止过大的输出值导致执行器过载 
    """

    def __init__(self, kp, ki, kd, integral_limit=None, output_limit=None):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0
        self.integral_limit = integral_limit
        self.output_limit = output_limit
"""
update 方法：计算控制器的输出值
error       误差
delta_time 时间差

"""
    def update(self, error, delta_time):
        # 积分项计算（带限幅）
        self.integral += error * delta_time
        
        if self.integral_limit:
            self.integral = max(-self.integral_limit, min(self.integral_limit, self.integral))
        
        # 微分项计算
        derivative = (error - self.prev_error) / delta_time if delta_time > 0 else 0
        self.prev_error = error
        
        # 输出计算（带限幅）
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        if self.output_limit: 

            output = max(-self.output_limit, min(self.output_limit, output))
        return output
    
    
#clamp 函数：用于确保某个值在一个指定的范围内，如果值超出了范围，就将其限制在最大或最小值之间。
def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

# PID参数初始化
angle_pid = PID(kp=15.0, ki=0.0, kd=2.0, output_limit=500)   # 直立环（PD控制）
speed_pid = PID(kp=3.0, ki=0.5, kd=0.0, output_limit=5.0)    # 速度环（PI控制）
steer_pid = PID(kp=4.0, ki=0.0, kd=0.5, output_limit=200)     # 转向环（PD控制）

balance_angle = 0.0   # 直立平衡目标角度
target_speed = 0.0    # 目标速度（0表示静止平衡）
max_pwm = 1000        # 电机PWM最大值

while True:
    dt = 0.01  # 控制周期10ms
    
    # 传感器数据获取（示例函数需实现）
    current_angle = get_angle()          # 当前车体倾角
    current_gyro = get_gyro()             # 当前角速度（陀螺仪）
    current_speed = get_speed()          # 当前平均速度
    steering_error = get_steering_error()# 转向偏差（如摄像头中线偏移）
    
    # 速度环计算（输出为角度补偿量）
    speed_error = current_speed - target_speed
    angle_adjust = speed_pid.update(speed_error, dt)
    
    # 直立环计算（目标角度 = 平衡角度 + 速度环补偿）
    target_angle = balance_angle + angle_adjust
    angle_error = current_angle - target_angle
    balance_output = angle_pid.kp * angle_error + angle_pid.kd * (-current_gyro)
    
    # 转向环计算
    steer_output = steer_pid.update(steering_error, dt)
    
    # 综合输出（差速转向）
    left_pwm = balance_output + steer_output
    right_pwm = balance_output - steer_output
    
    # PWM限幅并输出
    left_pwm = clamp(left_pwm, -max_pwm, max_pwm)
    right_pwm = clamp(right_pwm, -max_pwm, max_pwm)
    set_motor(left_pwm, right_pwm)