"""Служебный скрипт (НЕ часть лабы): прогоняет CLI по заранее заданным ответам
и печатает их так, как будто их набрал человек, — для скриншотов в отчёт."""
import builtins, sys
answers = iter(line.rstrip("\n") for line in open(sys.argv[1], encoding="utf-8"))
def fake_input(prompt=""):
    try:
        answer = next(answers)
    except StopIteration:
        answer = "0"
    print(prompt + answer)
    return answer
builtins.input = fake_input
import main
main.main()
