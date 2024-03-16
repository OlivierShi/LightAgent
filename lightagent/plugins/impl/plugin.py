class Graphic:
    def __init__(self, name: str = "graphic"):
        self.name = name

    def draw_graphic(self, query: str):
        return f"Drawing graphic for {query}."
    
    def describe_graphic(self, image_link: str):
        return f"Describing graphic from {image_link}."