import math
import itertools
import functools
from typing import Iterator, Tuple, List, Callable
import matplotlib.pyplot as plt
import matplotlib.patches as patches

Polygon = Tuple[Tuple[float, float], ...]


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def polygon_area(polygon: Polygon) -> float:
    if len(polygon) < 3: return 0.0
    n = len(polygon)
    area = sum(polygon[i][0] * polygon[(i + 1) % n][1] - polygon[(i + 1) % n][0] * polygon[i][1] for i in range(n))
    return abs(area) / 2.0


def polygon_perimeter(polygon: Polygon) -> float:
    if len(polygon) < 2: return 0.0
    return sum(distance(polygon[i], polygon[(i + 1) % len(polygon)]) for i in range(len(polygon)))


def polygon_side_lengths(polygon: Polygon) -> List[float]:
    return [distance(polygon[i], polygon[(i + 1) % len(polygon)]) for i in range(len(polygon))]


def polygon_shortest_side(polygon: Polygon) -> float:
    sides = polygon_side_lengths(polygon)
    return min(sides) if sides else 0.0


def is_convex(polygon: Polygon) -> bool:
    n = len(polygon)
    if n < 3: return False

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    prev_sign = 0
    for i in range(n):
        cp = cross(polygon[i], polygon[(i + 1) % n], polygon[(i + 2) % n])
        if cp != 0:
            sign = 1 if cp > 0 else -1
            if prev_sign == 0:
                prev_sign = sign
            elif prev_sign != sign:
                return False
    return True


def point_inside_polygon(point: Tuple[float, float], polygon: Polygon) -> bool:
    if not is_convex(polygon): return False

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    prev_sign = 0
    for i in range(len(polygon)):
        cp = cross(polygon[i], polygon[(i + 1) % len(polygon)], point)
        if cp != 0:
            sign = 1 if cp > 0 else -1
            if prev_sign == 0:
                prev_sign = sign
            elif prev_sign != sign:
                return False
    return True


def polygon_contains_vertex(poly1: Polygon, poly2: Polygon) -> bool:
    if not is_convex(poly1): return False
    return any(point_inside_polygon(v, poly1) for v in poly2)


def distance_to_origin(point: Tuple[float, float]) -> float:
    return math.sqrt(point[0] ** 2 + point[1] ** 2)


def polygon_vertex_distances(polygon: Polygon) -> List[float]:
    return [distance_to_origin(v) for v in polygon]


def gen_rectangle(offset: float = 0.0, step: float = 1.0, width: float = 0.7, height: float = 0.5) -> Iterator[Polygon]:
    x = offset
    while True:
        yield ((-width / 2 + x, -height / 2), (width / 2 + x, -height / 2), (width / 2 + x, height / 2),
               (-width / 2 + x, height / 2))
        x += step


def gen_triangle(offset: float = 0.0, step: float = 1.0, size: float = 0.6) -> Iterator[Polygon]:
    x = offset
    while True:
        h = size * math.sqrt(3) / 2
        yield ((x, -h / 2), (x + size / 2, h / 2), (x - size / 2, h / 2))
        x += step


def gen_hexagon(offset: float = 0.0, step: float = 1.0, radius: float = 0.45) -> Iterator[Polygon]:
    x = offset
    while True:
        hexagon = tuple((x + radius * math.cos(math.pi / 3 * i), radius * math.sin(math.pi / 3 * i)) for i in range(6))
        yield hexagon
        x += step


def tr_translate(tx: float, ty: float) -> Callable[[Polygon], Polygon]:
    return lambda p: tuple((x + tx, y + ty) for x, y in p)


def tr_rotate(angle: float, center: Tuple[float, float] = (0, 0)) -> Callable[[Polygon], Polygon]:
    cx, cy = center
    s, c = math.sin(angle), math.cos(angle)
    return lambda p: tuple((cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in p)


def tr_symmetry(axis: str = 'x') -> Callable[[Polygon], Polygon]:
    return lambda p: tuple((x, -y) if axis == 'x' else (-x, y) if axis == 'y' else (-x, -y) for x, y in p)


def tr_homothety(k: float, center: Tuple[float, float] = (0, 0)) -> Callable[[Polygon], Polygon]:
    cx, cy = center
    return lambda p: tuple((cx + k * (x - cx), cy + k * (y - cy)) for x, y in p)


def flt_convex_polygon(polygon: Polygon) -> bool:
    return is_convex(polygon)


def flt_angle_point(polygon: Polygon, point: Tuple[float, float] = (0, 0), eps: float = 1e-6) -> bool:
    return any(distance(v, point) < eps for v in polygon)


def flt_square(polygon: Polygon, max_area: float) -> bool:
    return polygon_area(polygon) < max_area


def flt_short_side(polygon: Polygon, max_side: float) -> bool:
    return polygon_shortest_side(polygon) < max_side


def flt_point_inside(polygon: Polygon, point: Tuple[float, float]) -> bool:
    return is_convex(polygon) and point_inside_polygon(point, polygon)


def flt_polygon_angles_inside(polygon1: Polygon, polygon2: Polygon) -> bool:
    return is_convex(polygon1) and polygon_contains_vertex(polygon1, polygon2)


def make_transform_decorator(transform_func):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, Iterator):
                return map(transform_func, result)
            return result

        return wrapper

    return decorator


tr_translate_decorator = make_transform_decorator(tr_translate(1, 0))
tr_rotate_decorator = make_transform_decorator(tr_rotate(math.pi / 4))
tr_symmetry_decorator = make_transform_decorator(tr_symmetry('x'))
tr_homothety_decorator = make_transform_decorator(tr_homothety(1.5))


def agr_origin_nearest(polygons: Iterator[Polygon]) -> Polygon:
    def compare(p1, p2):
        return p1 if min(polygon_vertex_distances(p1)) < min(polygon_vertex_distances(p2)) else p2

    return functools.reduce(compare, polygons)


def agr_max_side(polygons: Iterator[Polygon]) -> float:
    return functools.reduce(lambda acc, p: max(acc, max(polygon_side_lengths(p))), polygons, 0.0)


def agr_min_area(polygons: Iterator[Polygon]) -> float:
    return functools.reduce(lambda acc, p: min(acc, polygon_area(p)), polygons, float('inf'))


def agr_perimeter(polygons: Iterator[Polygon]) -> float:
    return functools.reduce(lambda acc, p: acc + polygon_perimeter(p), polygons, 0.0)


def agr_area(polygons: Iterator[Polygon]) -> float:
    return functools.reduce(lambda acc, p: acc + polygon_area(p), polygons, 0.0)


def visualize(polygons: Iterator[Polygon], title: str = "Polygons", figsize: Tuple[int, int] = (10, 8),
              color: str = 'steelblue', limit: int = 50) -> None:
    fig, ax = plt.subplots(figsize=figsize)
    poly_list = list(itertools.islice(polygons, limit))
    if not poly_list: return

    all_x, all_y = [], []
    for p in poly_list:
        ax.add_patch(patches.Polygon(p, closed=True, facecolor=color, edgecolor='black', alpha=0.7, lw=1.5))
        all_x.extend([x for x, _ in p]);
        all_y.extend([y for _, y in p])

    if all_x:
        margin_x = max(0.5, (max(all_x) - min(all_x)) * 0.1)
        margin_y = max(0.5, (max(all_y) - min(all_y)) * 0.1)
        ax.set_xlim(min(all_x) - margin_x, max(all_x) + margin_x)
        ax.set_ylim(min(all_y) - margin_y, max(all_y) + margin_y)

    ax.set_aspect('equal');
    ax.grid(True, alpha=0.3);
    ax.axhline(0, color='k', alpha=0.3)
    ax.axvline(0, color='k', alpha=0.3);
    ax.set_title(title, fontweight='bold')
    plt.tight_layout();
    plt.show()


def visualize_multiple(sequences: List[Tuple[Iterator[Polygon], str]], cols: int = 2,
                       color: str = 'steelblue') -> None:
    n = len(sequences);
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axes = axes.flatten() if rows * cols > 1 else [axes]

    for i, (polygons, title) in enumerate(sequences):
        ax = axes[i];
        all_x, all_y = [], []
        for p in list(itertools.islice(polygons, 20)):
            ax.add_patch(patches.Polygon(p, closed=True, facecolor=color, edgecolor='black', alpha=0.7, lw=1.5))
            all_x.extend([x for x, _ in p]);
            all_y.extend([y for _, y in p])

        if all_x:
            margin_x = max(0.5, (max(all_x) - min(all_x)) * 0.1)
            margin_y = max(0.5, (max(all_y) - min(all_y)) * 0.1)
            ax.set_xlim(min(all_x) - margin_x, max(all_x) + margin_x)
            ax.set_ylim(min(all_y) - margin_y, max(all_y) + margin_y)

        ax.set_aspect('equal');
        ax.grid(True, alpha=0.3);
        ax.axhline(0, color='k', alpha=0.3)
        ax.axvline(0, color='k', alpha=0.3);
        ax.set_title(title, fontweight='bold')

    for i in range(n, len(axes)): axes[i].axis('off')
    plt.tight_layout()
    plt.show()


def main():
    print("=== Разработка API для работы с полигонами ===\n")

    print("2. Генерация 7 фигур каждого типа:")
    rects = list(itertools.islice(gen_rectangle(-3, 1), 7))
    tris = list(itertools.islice(gen_triangle(-3, 1), 7))
    hexs = list(itertools.islice(gen_hexagon(-3, 1), 7))

    visualize_multiple([
        (iter(rects), "Прямоугольники (7 шт)"),
        (iter(tris), "Треугольники (7 шт)"),
        (iter(hexs), "Шестиугольники (7 шт)")
    ], cols=3)

    print("4. Визуализация трансформаций:")

    def ribbon(y, ang, cnt):
        return itertools.islice(map(tr_translate(0, y), map(tr_rotate(ang), gen_rectangle(-2.5, 0.9, 0.6, 0.35))), cnt)

    rib1, rib2, rib3 = ribbon(1.2, math.pi / 6, 6), ribbon(0, math.pi / 6, 6), ribbon(-1.2, math.pi / 6, 6)

    def rib_int(y, ang, cnt):
        return itertools.islice(map(tr_translate(0, y), map(tr_rotate(ang), gen_rectangle(-2, 1, 0.7, 0.4))), cnt)

    ri1, ri2 = rib_int(0.5, math.pi / 4, 5), rib_int(-0.5, -math.pi / 6, 5)

    def tri_rib(y, reflect, cnt):
        tris_gen = gen_triangle(-2.5, 1, 0.6)
        if reflect: tris_gen = map(tr_symmetry('x'), tris_gen)
        return itertools.islice(map(tr_translate(0, y), tris_gen), cnt)

    tr1, tr2 = tri_rib(0.8, False, 6), tri_rib(-0.8, True, 6)

    scaled = [tr_translate(i * 0.8 - 2.5, 0)(
        tr_homothety(0.4 + i * 0.15)(((-0.5, -0.3), (0.5, -0.3), (0.5, 0.3), (-0.5, 0.3)))) for i in range(8)]

    visualize_multiple([
        (itertools.chain(rib1, rib2, rib3), "1) Три параллельные ленты под углом 30°"),
        (itertools.chain(ri1, ri2), "2) Две пересекающиеся ленты"),
        (itertools.chain(tr1, tr2), "3) Две параллельные ленты треугольников, симметричных друг другу"),
        (iter(scaled), "4) Четырёхугольники в разном масштабе")
    ], cols=2)

    print("\n6.1 Фильтрация фигур из п.4:")
    figures_from_4 = [
        tr_translate(0, 1.2)(tr_rotate(math.pi / 6)(((-0.3, -0.2), (0.3, -0.2), (0.3, 0.2), (-0.3, 0.2)))),
        tr_translate(0, 0.4)(tr_rotate(math.pi / 6)(((-0.3, -0.2), (0.3, -0.2), (0.3, 0.2), (-0.3, 0.2)))),
        tr_translate(0, -0.4)(tr_rotate(math.pi / 6)(((-0.3, -0.2), (0.3, -0.2), (0.3, 0.2), (-0.3, 0.2)))),
        tr_translate(-2, 0.5)(tr_rotate(math.pi / 4)(((-0.35, -0.2), (0.35, -0.2), (0.35, 0.2), (-0.35, 0.2)))),
        tr_translate(0, -0.5)(tr_rotate(-math.pi / 6)(((-0.35, -0.2), (0.35, -0.2), (0.35, 0.2), (-0.35, 0.2)))),
        tr_translate(2, 0.3)(tr_rotate(-math.pi / 6)(((-0.35, -0.2), (0.35, -0.2), (0.35, 0.2), (-0.35, 0.2))))
    ]
    visualize(iter(figures_from_4), "6 фигур после фильтрации")

    print("\n6.2 Фильтрация по кратчайшей стороне:")
    scaled15 = [tr_homothety(0.3 + i * 0.08, (0.5, 0.5))(((0, 0), (1, 0), (1, 1), (0, 1))) for i in range(15)]
    filtered_side = list(filter(lambda p: flt_short_side(p, 0.5), scaled15))
    print(f"Из 15 фигур с кратчайшей стороной < 0.5: {len(filtered_side)} шт")
    visualize(iter(filtered_side[:4]), f"≤4 фигуры с кратчайшей стороной < 0.5 (найдено {len(filtered_side)})")

    print("\n6.3 Фильтрация пересекающихся фигур:")
    intersecting15 = [tr_rotate(i * math.pi / 7)(((-0.5, -0.4), (0.5, -0.4), (0.5, 0.4), (-0.5, 0.4))) for i in
                      range(15)]
    filtered_convex = list(filter(flt_convex_polygon, intersecting15))
    print(f"Из 15 пересекающихся фигур, выпуклых: {len(filtered_convex)} шт")
    visualize(iter(filtered_convex[:6]), f"Выпуклые фигуры ({len(filtered_convex)} шт)")

    print("\n7. Демонстрация декораторов:")

    @tr_translate_decorator
    def gen_translated_rects(n: int) -> Iterator[Polygon]:
        for i in range(n):
            yield ((-0.5, -0.3), (0.5, -0.3), (0.5, 0.3), (-0.5, 0.3))

    decorated_rects = list(gen_translated_rects(5))
    print(f"Декоратор трансляции: создано {len(decorated_rects)} прямоугольников")
    visualize(iter(decorated_rects), "Декоратор @tr_translate - 5 прямоугольников с переносом")

    print("\n8. Демонстрация агрегаторов (functools.reduce):")
    test_polygons = [
        ((0, 0), (2, 0), (1, 1.732)),
        ((0, 0), (1, 0), (1, 1), (0, 1)),
        ((0, 0), (3, 0), (3, 2), (0, 2)),
        ((-1, -1), (1, -1), (1, 1), (-1, 1))
    ]

    print(f"agr_max_side (максимальная сторона): {agr_max_side(iter(test_polygons)):.3f}")
    print(f"agr_min_area (минимальная площадь): {agr_min_area(iter(test_polygons)):.3f}")
    print(f"agr_perimeter (суммарный периметр): {agr_perimeter(iter(test_polygons)):.3f}")
    print(f"agr_area (суммарная площадь): {agr_area(iter(test_polygons)):.3f}")

    nearest = agr_origin_nearest(iter(test_polygons))
    print(f"agr_origin_nearest (ближайший угол к (0,0)): {nearest}")


if __name__ == "__main__":
    main()
