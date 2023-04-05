# project: p3
# submitter: hyuan73@wisc.edu
# partner: none
# hours: 20
    
import time
import requests
import os
from selenium.webdriver.chrome.webdriver import WebDriver
import pandas as pd

class Parent:
    def twice(self):
        self.message()
        self.message()
        
    def message(self):
        print("parent says hi")
        
class Child(Parent):
    def message(self):
        print("child says hi")

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []
        self.queue = []
        
    def visit_and_get_children(self, node):
        """ Record the node value in self.order, and return its children
        param: node
        return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        # 1. clear out visited set and order list
        self.visited.clear()
        self.order.clear()
        
        # 2. start recursive search by calling dfs_visit
        self.dfs_visit(node)
        
    def dfs_visit(self, node):
        # 1. if this node has already been visited, just `return` (no value necessary)
        if node in self.visited:
            return
        
        # 2. mark node as visited by adding it to the set
        self.visited.add(node)
        #Matrix search mode, If file search mode, self.order should not append node but value
        if not node.endswith(".txt"):
            self.order.append(node)
        # 3. call self.visit_and_get_children(node) to get the children
        children = self.visit_and_get_children(node)
        
        # 4. in a loop, call dfs_visit on each of the children
        for child in children:
            self.dfs_visit(child)
            
    def bfs_search(self, node):
        # 1. clear out visited set and order list
        self.visited.clear()
        self.order.clear()
        
        # 2. start the BFS search by adding the starting node to the queue
        self.queue.append(node)
        
        # 3. while there are still nodes in the queue:
        while self.queue:
            current_node = self.queue.pop(0)
            if current_node in self.visited:
                continue
            self.visited.add(current_node)
            #Matrix search mode, If file search mode, self.order should not append node but value
            if not current_node.endswith(".txt"):
                self.order.append(current_node)
            children = self.visit_and_get_children(current_node)
            for child in children:
                if child not in self.visited:
                    self.queue.append(child)
        
        
class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__() # call constructor method of parent class
        self.df = df

    def visit_and_get_children(self, node):
        # TODO: Record the node value in self.order
        children = []
        # TODO: use `self.df` to determine what children the node has and append them
        for node, has_edge in self.df.loc[node].items():
            if has_edge == 1:
                children.append(node)
        return children

class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()
        
    def visit_and_get_children(self, node):
        with open(os.path.join('file_nodes', node)) as f:
            value = f.readline().strip()
            children = f.readline().strip().split(',')
            self.order.append(value)   
            return children
        
    def concat_order(self):
        return ''.join(self.order)

class WebSearcher(GraphSearcher):
    def __init__(self, driver: WebDriver):
        super().__init__()
        self.driver = driver
        self.tables = []
        
    def visit_and_get_children(self, node):
        self.driver.get(node)
        links = [a.get_attribute('href') for a in self.driver.find_elements_by_tag_name('a')]
        tables = pd.read_html(self.driver.page_source)
        self.tables.extend([tables[0]])
        return links
        
    def table(self):
        return pd.concat(self.tables, ignore_index=True)

def reveal_secrets(driver, url, travellog):
    # generate password
    i = 0
    passw = []
    while i < len(travellog['clue']) and travellog['clue'][i] is not None:
        passw.append(travellog['clue'][i])
        i += 1
        
    s = [str(i) for i in passw]
    password = int("".join(s))
    print(password)
    # visit url
    driver.get(url)

    # enter password and click "GO"
    password_input = driver.find_element("id", "password")
    password_input.send_keys(password)
    go_button = driver.find_element("id", "attempt-button")
    go_button.click()

    # wait for page to load
    time.sleep(3)

    # click "View Location" button
    view_location_button = driver.find_element("id", 'locationBtn')
    view_location_button.click()

    # wait for result to load
    time.sleep(3)

    # save image
    image_url = driver.find_element("id", 'image').get_attribute('src')
    response = requests.get(image_url)
    with open('Current_Location.jpg', 'wb') as f:
        f.write(response.content)

    # return current location
    return driver.find_element("id", 'location').text