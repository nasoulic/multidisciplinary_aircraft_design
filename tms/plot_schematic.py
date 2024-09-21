import matplotlib.pyplot as plt 

class box(object):

    def __init__(self):

        self.a = 1
        self.b = 1
        self.text = 'box'
        self.x = 0
        self.y = 0

    def edit_dimensions(self, a, b = 0):

        self.a = a
        if b > 0:
            self.b = b
        else:
            self.b = a

    def edit_name(self, name):

        self.text = name

    def set_position(self, offset_x, offset_y):

        x_init = [0, 1, 1, 0, 0]
        y_init = [0, 0, 1, 1, 0]

        self.x = [offset_x + self.a*i for i in x_init]
        self.y = [offset_y + self.b*i for i in y_init]

    def draw(self):

        plt.plot(self.x, self.y, color = 'k', linewidth = 1.2)
        plt.text(sum(self.x)/len(self.x), sum(self.y)/len(self.y), self.text, horizontalalignment = "center", verticalalignment = "center")

class pipes(object):

    def __init__(self):
        pass

    def connect_boxes(self, box1, box2):

        self.start_x = max(box1.x)
        self.end_x = min(box2.x)

        self.start_y = 0.5*(max(box1.y) + min(box1.y))
        self.end_y = 0.5*(max(box2.y) + min(box2.y))

    def draw(self):

        plt.plot([self.start_x, self.end_x], [self.start_y, self.end_y], color = 'k', linewidth = 2)


plt.figure(figsize = (8, 6))

a = 2.5


box1 = box()
box1.edit_dimensions(a)
box1.edit_name("HEX")
box1.set_position(12*box1.a, 2*box1.b)
box1.draw()


box2 = box()
box2.edit_dimensions(a)
box2.edit_name("Spliter")
box2.set_position(2*box2.a, 2*box2.b)
box2.draw()

box3 = box()
box3.edit_dimensions(a)
box3.edit_name("Bat.")
box3.set_position(box3.a*4, 0)
box3.draw()

box4 = box()
box4.edit_dimensions(a)
box4.edit_name("E-Motor")
box4.set_position(box4.a*4, box4.b*2)
box4.draw()

box5 = box()
box5.edit_dimensions(a)
box5.edit_name("Inv.")
box5.set_position(box5.a*6, box5.b*2)
box5.draw()

box6 = box()
box6.edit_dimensions(a)
box6.edit_name("E-Gen")
box6.set_position(box6.a*4, box6.b*4)
box6.draw()

box7 = box()
box7.edit_dimensions(a)
box7.edit_name("Conv.")
box7.set_position(box7.a*6, box7.b*4)
box7.draw()

box8 = box()
box8.edit_dimensions(a)
box8.edit_name("DC-DC")
box8.set_position(box8.a*8, box8.b*4)
box8.draw()

box9 = box()
box9.edit_dimensions(a)
box9.edit_name("Mixer")
box9.set_position(box9.a*10, box9.b*2)
box9.draw()

pipe23 = pipes()
pipe23.connect_boxes(box2, box3)
pipe23.draw()

pipe24 = pipes()
pipe24.connect_boxes(box2, box4)
pipe24.draw()

pipe26 = pipes()
pipe26.connect_boxes(box2, box6)
pipe26.draw()

pipe45 = pipes()
pipe45.connect_boxes(box4, box5)
pipe45.draw()

pipe67 = pipes()
pipe67.connect_boxes(box6, box7)
pipe67.draw()

pipe78 = pipes()
pipe78.connect_boxes(box7, box8)
pipe78.draw()

pipe91 = pipes()
pipe91.connect_boxes(box9, box1)
pipe91.draw()

pipe89 = pipes()
pipe89.connect_boxes(box8, box9)
pipe89.draw()

pipe59 = pipes()
pipe59.connect_boxes(box5, box9)
pipe59.draw()

pipe39 = pipes()
pipe39.connect_boxes(box3, box9)
pipe39.draw()

plt.axis("equal")
plt.show()