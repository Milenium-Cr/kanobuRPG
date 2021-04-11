import yaml
from random import uniform, randint

with open("yaml/settings.yaml") as f:
    data = yaml.safe_load(f.read())

with open("yaml/locale.yaml") as f:
    locale = yaml.safe_load(f.read())


class Game:
    def __init__(self):
        global rock, paper, scissors
        rock = Kanobu("rock")
        paper = Kanobu("paper")
        scissors = Kanobu("scissors")
        self.playerchoice = 0
        self.botchoice = 0

    def menu(self):
        while True:
            print(locale["menu"][0])
            print(locale["menu"][1])
            choice = input(">>> ")
            if choice in ["1", "2", "3"]:
                game.menu_choice(choice)
                break
            else:
                break

    def menu_choice(self, choice):
        if choice == "1":
            game.battle()
        if choice == "2":
            game.check_kanobu()
        if choice == "3":
            game.settings()

    def settings(self):
        while True:
            print("1. Восстановить здоровье")
            choice = input(">>> ")
            if choice in ["1"]:
                if int(choice) == 1:
                    game.regenerate_team()
            else:
                break

    def check_kanobu(self):
        list = [rock, paper, scissors]
        for x in list:
            if x.health <= 0:
                x.health = 0
                status_ = "[МЕРТВ] "
            else:
                status_ = ""
            print(locale["check"][0].format(
                status=status_,
                name=x.name,
                maxhealth=x.maxhealth,
                health=x.health,
                minattack=x.minattack,
                maxattack=x.maxattack,
                defence=x.defence,
                level=x.level,
                levelup_exp=x.levelup_exp,
                exp=round(x.exp, 1)
            ))
        print("\n")

    def init_enemy(self):
        global rock_enemy, paper_enemy, scissors_enemy

        rock_enemy = Kanobu("rock")
        paper_enemy = Kanobu("paper")
        scissors_enemy = Kanobu("scissors")

    def battle(self):
        self.init_enemy()
        items = [rock, scissors, paper]

        botitems = [rock_enemy, scissors_enemy, paper_enemy]
        teamlevel = rock.level + paper.level + scissors.level
        botlevel = rock_enemy.level + paper_enemy.level + scissors_enemy.level

        print(locale["battle"][0].format(teamlevel=teamlevel,
                                         botlevel=botlevel))

        while True:
            for item in botitems:
                if item.health <= 0:
                    botitems.remove(item)

            # начало боя и вывод текста
            print(locale["battle"][1])
            for i, item in enumerate(items):
                print(locale["battle"][2].format(
                    number=i+1,
                    kanobu=item.name,
                    health=item.health)
                )

            # выбор игрокв
            if len(items) == 0:
                self.lose()
                break

            while True:
                choice = input(">>> ")
                if int(choice)-1 in range(len(items)):
                    self.playerchoice = items[int(choice) - 1]
                    break

            # выбор бота
            if len(botitems) == 0:
                self.win()
                break

            try:
                self.botchoice = botitems[randint(0, len(botitems)-1)]
            except:
                self.win()
                break

            print(f"{self.playerchoice.name} | {self.botchoice.name}")
            self.step("attack")

            if len(botitems) == 1 and self.botchoice.health <= 0:
                self.win()
                break

            self.step("defence")
            try:
                for i in items:
                    if i.health <= 0:
                        items.remove(i)
            except:
                self.lose()

    def checkweakness(self, turn):
        weakness = [
            [rock, scissors],
            [scissors, paper],
            [paper, rock]
        ]

        for item in weakness:
            if turn == "player":
                if item == [self.botchoice.type, self.playerchoice.type]:
                    print(locale["battle"][3])
                    return 0.6
                else:
                    return 1
            elif turn == "bot":
                if item == [self.playerchoice.type, self.botchoice.type]:
                    return 0.6
                else:
                    return 1

    def step(self, action):
        source_damage = randint(self.playerchoice.minattack,
                                self.playerchoice.maxattack)

        if action == "attack":

            damage = source_damage * self.checkweakness("player") - self.botchoice.defence

            if damage <= 0:
                damage = 1

            self.botchoice.health -= damage

            print(locale["battle"][4].format(damage=damage))

            if self.botchoice.health <= 0:
                exp = ((4 + 1.3 * (self.playerchoice.level * 0.7) + (0.7 * randint(1, 5))) * uniform(0.8, 1.5)) * 0.9

                self.playerchoice.exp += exp

                print(locale["level"][0].format(
                    kanobu=self.playerchoice.name,
                    exp=round(exp, 1))
                )

        elif action == "defence":
            damage = source_damage * self.checkweakness("bot") - self.playerchoice.defence
            if damage <= 0:
                damage = 1
            self.playerchoice.health -= damage
            print(locale["battle"][5].format(
                playerchoice=self.playerchoice.name.lower(),
                damage=damage
            ))

    def win(self):
        items = [rock, scissors, paper]
        print("Победа!")
        for i in items:
            exp = i.exp * data["modifications"]["expirience"]["win"]
            print(locale["level"][1].format(
                kanobu=i.name,
                exp=round(exp - i.exp, 1),
                expbefore=round(i.exp, 1),
                expafter=round(exp, 1))
            )
        for i in items:
            i.level_up()

    def lose(self):
        items = [rock, scissors, paper]
        print("Поражение...")
        for i in items:
            exp = i.exp * data["modifications"]["expirience"]["lose"]
            print(locale["level"][2].format(
                kanobu=i.name,
                exp=round(exp - i.exp, 1),
                expbefore=round(i.exp, 1),
                expafter=round(exp, 1))
            )
            i.level_up()

    def regenerate_team(self):
        items = [rock, paper, scissors]
        for x in items:
            x.health = x.maxhealth
        print("Здоровье восстановлено.")


class Kanobu:
    def __init__(self, kanobu):
        self.type = kanobu
        self.name = locale["kanobu"][kanobu]
        self.init_stats()

    def init_stats(self):
        self.maxhealth = data["stats"][self.type]["health"]
        self.health = self.maxhealth
        self.minattack = data["stats"][self.type]["damage"]["min"]
        self.maxattack = data["stats"][self.type]["damage"]["max"]
        self.defence = data["stats"][self.type]["defence"]
        self.level = 1
        self.exp = 0
        self.levelup_exp = data["stats"][self.type]["levelup_exp"]

    def level_up(self):
        while True:
            if self.exp >= self.levelup_exp:
                self.exp -= self.levelup_exp
                self.level += 1

                statsup = data["modifications"]["statsup"]

                health_up = randint(statsup["health"]["min"],
                                    statsup["health"]["max"])

                minattack_up = randint(statsup["attack"]["min"],
                                       statsup["attack"]["max"])

                maxattack_up = randint(statsup["attack"]["min"],
                                       statsup["attack"]["max"])

                defence_up = randint(statsup["defence"]["min"],
                                     statsup["defence"]["max"])

                levelexp_up = randint(statsup["exp"]["min"],
                                      statsup["exp"]["max"])

                self.maxhealth += health_up
                self.minattack += minattack_up
                self.maxattack += maxattack_up
                self.defence += defence_up
                self.levelup_exp += levelexp_up

                print(locale["stats"][0].format(
                    kanobu=self.name,
                    level=self.level)
                )

                print(locale["stats"][1].format(
                    health=self.maxhealth - health_up,
                    newhealth=self.maxhealth)
                )

                print(locale["stats"][2].format(
                    minattack=self.minattack - minattack_up,
                    newminattack=self.minattack)
                )

                print(locale["stats"][3].format(
                    maxattack=self.maxattack - maxattack_up,
                    newmaxattack=self.maxattack)
                )

                print(locale["stats"][4].format(
                    defence=self.defence - defence_up,
                    newdefence=self.defence)
                )

                print(locale["stats"][5].format(
                    level=self.level+1,
                    exp=self.levelup_exp - levelexp_up,
                    newexp=self.levelup_exp)
                )

                if self.minattack > self.maxattack:
                    self.minattack = self.maxattack
            else:
                break


game = Game()

while True:
    game.menu()
