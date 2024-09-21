class InterX(object):

    def __init__(self):
        pass

    def orientation(self, p, q, r):
        """
        Function to find the orientation of three points (p, q, r).
        Returns the following values:
        0 -> Collinear
        1 -> Clockwise
        2 -> Counterclockwise
        """
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0:
            return 0
        return 1 if val > 0 else 2

    def on_segment(self, p, q, r):
        """
        Check if point q lies on line segment pr.
        """
        if (
            (q[0] <= max(p[0], r[0]))
            and (q[0] >= min(p[0], r[0]))
            and (q[1] <= max(p[1], r[1]))
            and (q[1] >= min(p[1], r[1]))
        ):
            return True
        return False

    def do_intersect(self, p1, q1, p2, q2):
        """
        Main function to check if two line segments (p1,q1) and (p2,q2) intersect.
        """
        o1 = self.orientation(p1, q1, p2)
        o2 = self.orientation(p1, q1, q2)
        o3 = self.orientation(p2, q2, p1)
        o4 = self.orientation(p2, q2, q1)

        if o1 != o2 and o3 != o4:
            return True

        if o1 == 0 and self.on_segment(p1, p2, q1):
            return True

        if o2 == 0 and self.on_segment(p1, q2, q1):
            return True

        if o3 == 0 and self.on_segment(p2, p1, q2):
            return True

        if o4 == 0 and self.on_segment(p2, q1, q2):
            return True

        return False

    def intersection_point(self, p1, q1, p2, q2):
        """
        Function to find the intersection point of two line segments (p1,q1) and (p2,q2).
        Returns None if the segments don't intersect.
        """
        if self.do_intersect(p1, q1, p2, q2):
            A1 = q1[1] - p1[1]
            B1 = p1[0] - q1[0]
            C1 = A1 * p1[0] + B1 * p1[1]

            A2 = q2[1] - p2[1]
            B2 = p2[0] - q2[0]
            C2 = A2 * p2[0] + B2 * p2[1]

            determinant = A1 * B2 - A2 * B1

            x = (B2 * C1 - B1 * C2) / determinant
            y = (A1 * C2 - A2 * C1) / determinant

            return (x, y)

        return None
    
def sum_values_up_to_key(input_dict, key):
    total = 0
    for k, v in input_dict.items():
        if k == key:
            total += v
            break  # Stop when you reach the specified key
        total += v
    return total