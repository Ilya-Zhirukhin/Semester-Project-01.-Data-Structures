
class FibonacciHeap:
    # класс внутреннего узла
    class Node:
        def __init__(self, data):
            self.data = data
            self.parent = self.child = self.left = self.right = None
            self.degree = 0
            self.mark = False

    # функция для перебора двусвязного списка
    def iterate(self, head):
        node = stop = head
        flag = False
        while True:
            if node == stop and flag is True:
                break
            elif node == stop:
                flag = True
            yield node
            node = node.right

    # указатель на головной и минимальный узел в корневом списке
    root_list, min_node = None, None

    # для того чтобы поддерживать общее количество узлов в полной куче Фибоначчи
    total_nodes = 0

    # вернуть минимальный узел за время O(1)
    def find_min(self):
        return self.min_node

    # извлечь (удалить) минимальный узел из кучи за время O(log n)
    # анализ амортизированной сложности можно найти здесь (http://bit.ly/1ow1Clm)
    def extract_min(self):
        z = self.min_node
        if z is not None:
            if z.child is not None:
                # attach child nodes to root list
                children = [x for x in self.iterate(z.child)]
                for i in range(0, len(children)):
                    self.merge_with_root_list(children[i])
                    children[i].parent = None
            self.remove_from_root_list(z)
            # set new min node in heap
            if z == z.right:
                self.min_node = self.root_list = None
            else:
                self.min_node = z.right
                self.consolidate()
            self.total_nodes -= 1
        return z

    # вставить новый узел в неупорядоченный корневой список за время O(1)
    def insert(self, data):
        n = self.Node(data)
        n.left = n.right = n
        self.merge_with_root_list(n)
        if self.min_node is None or n.data < self.min_node.data:
            self.min_node = n
        self.total_nodes += 1

    # изменить данные(понизить ключ) некоторого узла в куче за время O (1)
    def decrease_key(self, x, k):
        if k > x.data:
            return None
        x.data = k
        y = x.parent
        if y is not None and x.data < y.data:
            self.cut(x, y)
            self.cascading_cut(y)
        if x.data < self.min_node.data:
            self.min_node = x

    # объединить две кучи Фибоначчи за время O (1) путем объединения корневых списков
    # корень нового корневого списка становится равным первому списку и второму
    # список просто добавляется в конец (затем определяется правильный минимальный узел)
    def merge(self, h2):
        H = FibonacciHeap()
        H.root_list, H.min_node = self.root_list, self.min_node
        # исправить указатели в случае объединении двух куч
        last = h2.root_list.left
        h2.root_list.left = H.root_list.left
        H.root_list.left.right = h2.root_list
        H.root_list.left = last
        H.root_list.left.right = H.root_list
        # обновить минимальный узел, если необходимо
        if h2.min_node.data < H.min_node.data:
            H.min_node = h2.min_node
        # обновить общее количество узлов
        H.total_nodes = self.total_nodes + h2.total_nodes
        return H

    # если дочерний узел становится меньше своего родительского узла, мы
    # отсекаем этот дочерний узел и переносим его в корневой список
    def cut(self, x, y):
        self.remove_from_child_list(y, x)
        y.degree -= 1
        self.merge_with_root_list(x)
        x.parent = None
        x.mark = False

    # каскадное сокращение родительского узла для получения хороших временных границ
    def cascading_cut(self, y):
        z = y.parent
        if z is not None:
            if y.mark is False:
                y.mark = True
            else:
                self.cut(y, z)
                self.cascading_cut(z)

    # объединить корневые узлы равной степени для консолидации кучи
    # путем создания списка неупорядоченных биномиальных деревьев
    def consolidate(self):
        A = [None] * self.total_nodes
        nodes = [w for w in self.iterate(self.root_list)]
        for w in range(0, len(nodes)):
            x = nodes[w]
            d = x.degree
            while A[d] != None:
                y = A[d]
                if x.data > y.data:
                    temp = x
                    x, y = y, temp
                self.heap_link(y, x)
                A[d] = None
                d += 1
            A[d] = x
        # найти новый минимальный узел - нет необходимости реконструировать новый корневой список ниже
        # потому что корневой список итеративно менялся по мере того, как мы перемещали
        # узлы в указанном выше цикле
        for i in range(0, len(A)):
            if A[i] is not None:
                if A[i].data < self.min_node.data:
                    self.min_node = A[i]

    # фактическая привязка одного узла к другому в корневом списке
    # одновременно обновляя дочерний связанный список
    def heap_link(self, y, x):
        self.remove_from_root_list(y)
        y.left = y.right = y
        self.merge_with_child_list(x, y)
        x.degree += 1
        y.parent = x
        y.mark = False

    # merge a node with the doubly linked root list
    def merge_with_root_list(self, node):
        if self.root_list is None:
            self.root_list = node
        else:
            node.right = self.root_list.right
            node.left = self.root_list
            self.root_list.right.left = node
            self.root_list.right = node

    # объединить узел с двусвязным корневым списком
    def merge_with_child_list(self, parent, node):
        if parent.child is None:
            parent.child = node
        else:
            node.right = parent.child.right
            node.left = parent.child
            parent.child.right.left = node
            parent.child.right = node

    # удалить узел из двусвязного корневого списка
    def remove_from_root_list(self, node):
        if node == self.root_list:
            self.root_list = node.right
        node.left.right = node.right
        node.right.left = node.left

    # удалить узел из двусвязного дочернего списка
    def remove_from_child_list(self, parent, node):
        if parent.child == parent.child.right:
            parent.child = None
        elif parent.child == node:
            parent.child = node.right
            node.right.parent = parent
        node.left.right = node.right
        node.right.left = node.left