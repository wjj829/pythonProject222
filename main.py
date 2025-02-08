import pygame
import random
import sys
# 游戏配置常量
WINDOW_WIDTH = 450  # 窗口宽度
WINDOW_HEIGHT = 500  # 窗口高度
GRID_SIZE = 50  # 每个格子的大小（需与图片尺寸匹配）
ROWS = 8  # 游戏区域行数
COLS = 8  # 游戏区域列数
IMAGES = [  # 方块图片路径
    't1.jpg',
    't2.jpg',
    't3.jpg',
    't4.jpg',
    't5.jpg'
]

class BlockGame:
    '''主游戏类'''

    def __init__(self):
        # Pygame初始化
        pygame.init()
        pygame.mixer.init()

        # 创建游戏窗口
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("开心消消乐")
        # 加载资源
        self.load_resources()

        # 游戏状态初始化
        self.reset_game()

        # 游戏时钟
        self.clock = pygame.time.Clock()

    def load_resources(self):
        """加载游戏资源"""
        try:                            #try块，用于尝试执行下面的代码
            # 加载方块图片并调整大小
            self.block_images = [        #初始化一个空列表，用于存储加载并调整大小后的方块图片
                pygame.transform.scale(      #此函数用于调整图片大小
                    pygame.image.load(Img),   #用于加载图片
                    size=(GRID_SIZE - 2, GRID_SIZE - 2)
                ) for Img in IMAGES
            ]
        except Exception as e:
            print("资源加载失败:", e)  #e用来储存捕获到的异常对象
            sys.exit()

    def reset_game(self):
        # 初始化游戏状态
        self.grid = [[0] * COLS for _ in range(ROWS)]  # 初始化一个全为0的二维列表,用于存储方块的位置
        self.selected = None  # 当前选中的方块坐标
        # 生成方块并确保没有连续的三个或更多相同方块
        for row in range(ROWS):
            for col in range(COLS):
                while True:
                    # 随机生成一个方块索引
                    block_index = random.randint(0, len(self.block_images) - 1)
                    # 检查当前方块是否会导致连续三个或更多相同方块
                    if not self._check_if3inline(row, col, block_index):
                        self.grid[row][col] = block_index
                        break

    def _check_if3inline(self, row, col, block_index):
        #检查放置当前方块后是否会导致连续三个或更多相同方块
        # 检查水平方向
        if col >= 2 and self.grid[row][col - 1] == block_index and self.grid[row][col - 2] == block_index:
            return True
        if col <= COLS - 3 and self.grid[row][col + 1] == block_index and self.grid[row][col + 2] == block_index:
            return True
        # 检查垂直方向
        if row >= 2 and self.grid[row - 1][col] == block_index and self.grid[row - 2][col] == block_index:
            return True
        if row <= ROWS - 3 and self.grid[row + 1][col] == block_index and self.grid[row + 2][col] == block_index:
            return True
        return False#当上述均未执行时，便返回False,意味着没有三个及以上连着的方块
    def draw_grid(self):
        """绘制游戏界面"""
        # 绘制淡蓝色背景
        self.screen.fill((173, 216, 230))

        # 绘制所有方块
        for row in range(ROWS):
            for col in range(COLS):
                # 计算绘制位置（留出顶部50像素显示分数）
                x = col * GRID_SIZE + 1
                y = row * GRID_SIZE + 50

                # 绘制方块图片
                self.screen.blit(
                self.block_images[self.grid[row][col]],
                dest=(x,y)
                )

                # 绘制选中框（黄色边框）
                if self.selected == (row, col):
                    pygame.draw.rect(   #绘制矩形函数
                        self.screen,    #指定绘制矩形的目标表面
                        color=(255,255,0),#颜色由GRB值指定，对应于黄色
                        rect=(x-2,y-2,GRID_SIZE+2,GRID_SIZE+2),#(x-2,y-2)是矩形的左上角坐标
                        width=3#矩形边框的宽度
                    )
    def find_matches(self):
        #查找所有可以消除的方块
        matches = set()#初始化一个空集合，用于存储可以消除的方块的坐标

        # 横向检测（三连及以上）
        for row in range(ROWS):
            for col in range(COLS - 2):
                if self.grid[row][col] == self.grid[row][col + 1] == self.grid[row][col + 2]:
                    matches.update({(row, col), (row, col + 1), (row, col + 2)})

        # 纵向检测（三连及以上）
        for col in range(COLS):
            for row in range(ROWS - 2):
                if self.grid[row][col] == self.grid[row + 1][col] == self.grid[row + 2][col]:
                    matches.update({(row, col), (row + 1, col), (row + 2, col)})

        return matches

    def remove_matches(self, matches):#定义一个方法，该方法接受一个参数matches
        #处理消除和下落逻辑
        removed = [[0] * COLS for _ in range(ROWS)]# 初始化一个列表，标记需要消除的方块
        for (row, col) in matches:#遍历matches集合中的每个坐标，将removed列表中相应值设为1
            removed[row][col] = 1

        # 处理每列的下落
        for col in range(COLS):
            remaining = []# 初始化一个空列表，用于收集未消除的方块（从下往上）
            for row in reversed(range(ROWS)):#reverse是为了实现从最后一行向上遍历所有行
                if not removed[row][col]:
                    remaining.append(self.grid[row][col])

            # 补充新方块到顶部
            remaining += [
                random.randint(0, len(self.block_images) - 1)#生成一个随机数，用于从图片列表中选择一个方块图像
                for _ in range(ROWS - len(remaining))#根据需要补充的方块数量生成一个包含随机方块索引的列表，并将其添加到remaining列表中。
            ]

            # 更新列数据（反转回正常顺序）
            for row in range(ROWS):
                self.grid[row][col] = remaining[ROWS - 1 - row]#从末尾开始取值才能实现反转顺序

    def swap_blocks(self, pos1, pos2):
        """交换两个方块的位置"""
        row1, col1 = pos1
        row2, col2 = pos2
        self.grid[row1][col1], self.grid[row2][col2] =  self.grid[row2][col2], self.grid[row1][col1]

    def handle_click(self, mouse_pos):
        #处理鼠标点击事件
        x, y = mouse_pos
        col = x // GRID_SIZE
        row = (y - 50) // GRID_SIZE  # 减去顶部留空

        # 检查点击是否在有效区域
        if 0 <= row < ROWS and 0 <= col < COLS:
            if not self.selected:
                # 第一次选择方块
                self.selected = (row, col)
            else:#如果已经选择了方块，将进入此步
                # 检查是否是相邻方块
                if (abs(self.selected[0] - row) +
                    abs(self.selected[1] - col)) == 1:#这里使用曼哈顿距离（即两个坐标在水平和垂直方向上的距离之和）来判断是否相邻。

                    # 执行交换
                    self.swap_blocks(self.selected, (row, col))

                    # 检查是否有可消除的方块
                    matches = self.find_matches()
                    if not matches:
                        # 没有匹配则交换回来
                        self.swap_blocks(self.selected, (row, col))
                    else:
                        # 处理消除和下落
                        while matches:#使用while循环处理消除和下落，直到没有更多的方块可以消除
                            self.remove_matches(matches)
                            matches = self.find_matches()
                # 清除选中状态
                self.selected = None
    def run(self):
        #游戏主循环
        running = True#用于控制游戏循环是否继续
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:#假如用户点了关闭按钮
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:#假如用户点击鼠标
                        self.handle_click(pygame.mouse.get_pos())
            # 更新画面
            self.draw_grid()
            pygame.display.update()#使用pygame.display.update()更新整个待显示的 Surface 对象到屏幕上
            self.clock.tick(10)  # 控制帧率 即游戏每秒最多更新的次数
        pygame.quit()
        sys.exit()

if __name__ == "__main__":#这行代码检查当前脚本是否作为主程序运行。如果是，那么下面的代码块将会被执行
    game = BlockGame()
    game.run()

