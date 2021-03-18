import numpy as np
import sys, math
t_max_value = 1000
max_epsilon = 100

def print_to_stdout(*a):
    sys.stdout.reconfigure(encoding='utf-8')
    print(*a, file=sys.stdout)


def run_big_quick(points, vels, T, S, P):
    particle = {}
    num_of_collision = 0
    for k in range(len(points)):
        particle[k] = 1
        point = points[k]
        vel = vels[k] * T
        p = point + vel
        p_collision = calc_collision(p, 2*S)
        for _ in range(p_collision):
            particle[k] *= P
        num_of_collision += p_collision

    return num_of_collision, particle

def calc_collision(point, bounds):
    num_of_col = 0
    x_col = 0
    y_col = 0
    first_hit = math.fabs(point[0]) - bounds / 2

    if first_hit > 0:
        x_col = 1 + math.fabs(first_hit) // bounds

    first_hit = math.fabs(point[1]) - bounds / 2

    if first_hit > 0:
        y_col = 1 + math.fabs(first_hit) // bounds

    num_of_col += x_col
    num_of_col += y_col
    return int(num_of_col)


def dist_origin(p):
    return p[0]*p[0] + p[1]*p[1]


def calc_beginning_of_time(points, reverse_vels, S):
    epsilon = 1
    t = 1
    while epsilon < max_epsilon:
        t = 1
        while t < t_max_value:
            prev_points = points + reverse_vels*t

            all_in_epsilon = True
            for p in prev_points:
                dist = dist_origin(p)
                if not check_is_in_epsilon(dist, epsilon):
                    all_in_epsilon = False
                    break
            if all_in_epsilon:
                break
            else:
                t += 1

        if t >= t_max_value:
            epsilon += 1
        else:
            break

    return t


def check_is_in_epsilon(value, epsilon):
    return -epsilon <= value <= epsilon

if __name__ == '__main__':

    N, S, T, P = input().split()
    N = int(N)
    S = int(S)
    T = int(T)
    P = float(P)

    points = []
    vels = []

    for i in range(N):
        px, py, vx, vy = input().split()
        points.append([float(px), float(py)])
        vels.append([float(vx), float(vy)])

    points = np.array(points)
    vels = np.array(vels)

    num_of_collision, particle = run_big_quick(points,vels, T, S, P)

    reverse_vels = vels * -1
    beginning_of_time = calc_beginning_of_time(points, reverse_vels, S)

    if beginning_of_time >= t_max_value:
        beginning_of_time = -1

    print_to_stdout(beginning_of_time, num_of_collision, sum(particle.values()))
