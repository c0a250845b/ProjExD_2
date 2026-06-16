import math
import os
import random
import sys
import time

import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP:    (0, -5),
    pg.K_DOWN:  (0, +5),
    pg.K_LEFT:  (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を5秒間表示する関数

    引数：スクリーンSurface
    戻り値：なし
    """
    black_surf = pg.Surface((WIDTH, HEIGHT))
    black_surf.set_alpha(128)
    black_surf.fill((0, 0, 0))
    screen.blit(black_surf, [0, 0])  # まず黒幕をscreenに貼り，その上に描画する

    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    font = pg.font.Font(None, 80)
    go_surf = font.render("Game Over", True, (255, 255, 255))

    go_x = (WIDTH - go_surf.get_width()) // 2
    go_y = HEIGHT // 2 - go_surf.get_height() // 2
    cry_y = go_y + (go_surf.get_height() - cry_img.get_height()) // 2

    screen.blit(cry_img, (go_x - cry_img.get_width() - 10, cry_y))
    screen.blit(cry_img, (go_x + go_surf.get_width() + 10, cry_y))
    screen.blit(go_surf, (go_x, go_y))

    pg.display.update()
    time.sleep(5)


def calc_orientation(
    org: pg.Rect,
    dst: pg.Rect,
    current_xy: tuple[float, float],
) -> tuple[float, float]:
    """
    爆弾からこうかとんへの方向ベクトルを計算して返す関数

    引数：
        org：爆弾Rect
        dst：こうかとんRect
        current_xy：現在の移動方向ベクトル
    戻り値：正規化された方向ベクトル or 現在の方向ベクトル
    """
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    norm = math.sqrt(dx ** 2 + dy ** 2)
    if norm < 300:
        return current_xy
    scale = math.sqrt(50) / norm
    return dx * scale, dy * scale


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルと対応するこうかとんSurfaceの辞書を返す関数

    戻り値：移動量タプルをキー，rotozoomしたSurfaceを値とした辞書
    """
    base_img = pg.image.load("fig/3.png")
    return {
        (0, 0):   pg.transform.rotozoom(base_img, 0, 0.9),
        (+5, 0):  pg.transform.rotozoom(base_img, 0, 0.9),
        (+5, -5): pg.transform.rotozoom(base_img, 45, 0.9),
        (0, -5):  pg.transform.rotozoom(base_img, 90, 0.9),
        (-5, -5): pg.transform.rotozoom(base_img, 135, 0.9),
        (-5, 0):  pg.transform.flip(pg.transform.rotozoom(base_img, 0, 0.9), True, False),
        (-5, +5): pg.transform.rotozoom(base_img, -135, 0.9),
        (0, +5):  pg.transform.rotozoom(base_img, -90, 0.9),
        (+5, +5): pg.transform.rotozoom(base_img, -45, 0.9),
    }


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズの異なる爆弾Surfaceのリストと加速度のリストを返す関数

    戻り値：爆弾SurfaceリストとaccリストのTuple
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)
    bb_accs = list(range(1, 11))
    return bb_imgs, bb_accs


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトのRectが画面内かどうかを判定する関数

    引数：こうかとんRect or 爆弾Rect
    戻り値：タプル（横方向判定結果，縦方向判定結果）
        画面内ならTrue，画面外ならFalse
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = +5.0, +5.0

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        screen.blit(bg_img, [0, 0])

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, (dx, dy) in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += dx
                sum_mv[1] += dy
        kk_img = kk_imgs[tuple(sum_mv)]
        kk_rct.move_ip(sum_mv)
        yoko, tate = check_bound(kk_rct)
        if not yoko:
            kk_rct.move_ip(-sum_mv[0], 0)
        if not tate:
            kk_rct.move_ip(0, -sum_mv[1])

        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        bb_rct.width = bb_img.get_width()
        bb_rct.height = bb_img.get_height()
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx = -vx
        if not tate:
            vy = -vy
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
