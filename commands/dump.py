from aiomultiprocess import Worker

async def main(state):

    print("modifying state here")

    print(state)

    print("heloo")
    print("stupid")
    print("stupid3")

    return "Modified this" + "blablablabla"