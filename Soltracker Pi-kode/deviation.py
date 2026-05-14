
def deviation(current_az, current_alt, target_az, target_alt):
    dev_az = target_az - current_az
    dev_alt = target_alt - current_alt
    return dev_az, dev_alt

# Positiv dev_az -> Må flytte kameravinkel mot høyre
# Positiv dev_alt -> Må flytte kameravinkel oppover
