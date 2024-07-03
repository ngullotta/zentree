from zentree import Screen

if __name__ == "__main__":
    try:
        tree = Screen()
        tree.start()
    except KeyboardInterrupt:
        pass
    finally:
        tree.stop()
