import os

def background_image_list(image_folder, n = 60):
    image_list = []
    image_folder = os.path.join(os.getcwd(), image_folder)
    for i in range(1,n+1):
        if i < 10:  
            test_name = 'test000' + str(i) + '.jpg'
            filename = os.path.join(image_folder, test_name)
            image_list.append(filename)
        elif i > 10 and i < 100:
            test_name = 'test00' + str(i) + '.jpg'
            filename = os.path.join(image_folder, test_name)
            image_list.append(filename)
        elif i > 100 and i < 1000:
            test_name = 'test0' + str(i) + '.jpg'
            filename = os.path.join(image_folder, test_name)
            image_list.append(filename)
        else:
            test_name = 'test' + str(i) + '.jpg'
            filename = os.path.join(image_folder, test_name)
            image_list.append(filename)
    
    return image_list

def test_image_list(image_folder, start = 85, end = 95):
    image_list = []
    image_folder = os.path.join(os.getcwd(), image_folder)
    for i in range(start,end+1):
        if i < 10:  
            test_name = 'test000' + str(i) + '.jpg'
            filename = os.path.join(image_folder, test_name)
            image_list.append(filename)
        else:
            test_name = 'test00' + str(i) + '.jpg'
            filename = os.path.join(image_folder, test_name)
            image_list.append(filename)
    
    return image_list