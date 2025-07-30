def congestion_estimation(speed_data):
    total_speed = 0
    num_speeds = 0
    average_speed=0

    # Calculate the average speed
    for mode, speed in speed_data.items():
        total_speed += speed
        num_speeds += 1
    
        
    if num_speeds >0:
        average_speed = total_speed / num_speeds
    

    # Determine congestion state using average speed 
    if 0 < average_speed <= 20:
        congestion_level = "1"
    elif 20 < average_speed <= 40:
        congestion_level = "2"
    elif 40 < average_speed <= 60:
        congestion_level = "3"
    elif 60 < average_speed:
        congestion_level = "4"
    else:
        congestion_level = "-1"

    return congestion_level, average_speed  # Return both values
