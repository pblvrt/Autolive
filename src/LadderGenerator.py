
class LadderGenerator:
    """
    def __init__(self, input_width, input_height, input_bitrate, input_fps):
        self.input_bitrate = input_bitrate
        self.input_width = input_width
        self.input_height = input_height
        self.input_fps = input_fps
    """ 

    def generate(self, input_width, input_bitrate, input_audio_bitrate, input_fps, return_Array):
        if input_width < 234 or input_bitrate < 145:
            return return_Array
        
        if input_width < 540 and input_fps > 30:
            input_fps = 30
        
        if input_bitrate > 5000:
            input_bitrate = 5000
            
        if input_width == 320:
            input_width = 360
        
        if input_bitrate <= 3000:
            input_audio_bitrate = 96000
        
        if round((input_width*16)/9)%2 == 0:
            height = round((input_width*16)/9)
        else:
            height = round((input_width*16)/9) + 1
            
        item = {
            'name': str(input_width),
            'width': round(input_width),
            'height': height,
            'bitrate': round(input_bitrate),
            'fps': input_fps,
            'audio_bitrate': input_audio_bitrate
        }
        
        return_Array.append(item)
        
        return self.generate(input_width/1.5, input_bitrate/1.3, input_audio_bitrate, input_fps, return_Array)


"""
# Tests
test = LadderGenerator()
value = test.generate(1080, 7800, 192000, 60, [])
print(value)
"""
