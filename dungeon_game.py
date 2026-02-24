#!/usr/bin/env python3
"""
  DUNGEON OF THE FORGOTTEN KING
  Full Creative Overhaul v2 — The name is on the tip of your tongue.
"""

import random
import os
import sys
import time
import dungeon_ascii_art

# ─────────────────────────────────────────────────────────────────────────────
# ANSI Color helpers
# ─────────────────────────────────────────────────────────────────────────────

class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

def clr(*codes):
    return "".join(codes)

def colored(text, *codes):
    return clr(*codes) + str(text) + C.RESET

def hr(char="─", width=62, color=C.DIM):
    return colored(char * width, color)

def clear():
    # ANSI escape — works in Docker/PTY without needing the `clear` binary
    if os.name == "nt":
        os.system("cls")
    else:
        print("\033[H\033[2J\033[3J", end="", flush=True)

def pause(msg="  [Press Enter to continue]"):
    input(colored(f"\n{msg}", C.DIM))

def slow_print(text, delay=0.022):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

# ─────────────────────────────────────────────────────────────────────────────
# Items
# ─────────────────────────────────────────────────────────────────────────────

class Item:
    def __init__(self, name, kind, value, desc, effect=None):
        self.name   = name
        self.kind   = kind    # weapon | armor | potion | key | misc
        self.value  = value
        self.desc   = desc
        self.effect = effect

ITEMS = {
    # Weapons
    "rusty_dagger":    Item("Rusty Dagger",     "weapon", 3,  "A worn blade. Better than bare hands."),
    "short_sword":     Item("Short Sword",       "weapon", 8,  "Reliable and balanced."),
    "battle_axe":      Item("Battle Axe",        "weapon", 14, "Heavy — but hits like a cart horse."),
    "kings_blade":     Item("King's Blade",      "weapon", 20, "Legendary sword of the Forgotten King.", "lifesteal"),
    # Armor
    "leather_armor":   Item("Leather Armor",     "armor",  3,  "Light protection, good mobility."),
    "chain_mail":      Item("Chain Mail",        "armor",  8,  "Solid steel links. A bit heavy."),
    "plate_armor":     Item("Plate Armor",       "armor",  14, "Heavy-gauge steel. Near impenetrable."),
    # Potions
    "health_potion":   Item("Health Potion",     "potion", 35, "Restores 35 HP."),
    "mega_potion":     Item("Mega Potion",       "potion", 70, "Restores 70 HP."),
    "strength_potion": Item("Strength Potion",   "potion", 12, "ATK +12 for 5 turns.", "str_boost"),
    # Keys
    "iron_key":        Item("Iron Key",          "key",    0,  "Opens the Treasure Vault."),
    "skull_key":       Item("Skull Key",         "key",    0,  "Opens the Throne Room."),
    # Misc — original
    "gold_coins":      Item("Gold Coins",        "misc",   40, "Clinking gold coins."),
    # Misc — new
    "kings_crown":     Item("King's Crown",      "misc",   80,
        "A crown for a man with no name. The jewels are still perfect. "
        "Someone kept polishing it. For centuries. Just in case."),
    "geralds_fish":    Item("Gerald's Fish",     "misc",    0,
        "A fish. From Gerald. He wanted you to have it. "
        "It smells like river water and something you might call regret if fish could regret things."),
    "haunted_lantern": Item("Haunted Lantern",   "misc",    5,
        "Still lit. You didn't light it. You've decided not to think too hard about this."),
    "ink_black_tome":  Item("Ink-Black Tome",    "misc",   10,
        "Contains detailed instructions for forgetting. Remarkably thorough. Also remarkably sad."),
    "final_letter":    Item("Final Letter",      "misc",    0,
        "A letter from whoever carved the warning on the antechamber wall."),
}

ITEM_COLOR = {
    "weapon": C.RED,
    "armor":  C.BLUE,
    "potion": C.GREEN,
    "key":    C.YELLOW,
    "misc":   C.WHITE,
}

# ─────────────────────────────────────────────────────────────────────────────
# Memory Fragments
# ─────────────────────────────────────────────────────────────────────────────

MEMORY_FRAGMENTS = {
    "frag_1": {
        "room_id": 1,
        "object":  "a cracked mosaic tile in the wall",
        "lore": (
            "  There was a king here. There was always a king here.\n"
            "  Nobody wrote down his name."
        ),
        "thought": (
            "  The face has been chipped away deliberately — carefully,\n"
            "  like they were doing the person a favor.\n"
            "  You don't think they were doing anyone a favor.\n"
            "\n  [Memory Fragment 1/7 collected]"
        ),
    },
    "frag_2": {
        "room_id": 2,
        "object":  "a soldier's commendation medal, face-down on a shelf",
        "lore": (
            "  Awarded for valor in the northern campaign,\n"
            "  by order of ________. The name was removed from\n"
            "  all medals by royal decree. The soldiers kept them anyway."
        ),
        "thought": (
            "  Someone was told to forget. They almost managed it.\n"
            "\n  [Memory Fragment 2/7 collected]"
        ),
    },
    "frag_3": {
        "room_id": 4,
        "object":  "a half-burned letter on the reading table",
        "lore": (
            "  \"...your sacrifice will not be forg—\" [remainder ash]\n"
            "  Someone tried to write it down.\n"
            "  The curse burned the ink as it dried."
        ),
        "thought": (
            "  Whatever comes after 'forg—' is gone.\n"
            "  You already know what it was going to say.\n"
            "\n  [Memory Fragment 3/7 collected]"
        ),
    },
    "frag_4": {
        "room_id": 3,
        "object":  "a scrap of parchment wedged under a crate",
        "lore": (
            "  A child's drawing: a crown, a smiling figure, the word 'papa'.\n"
            "  Goblins can't read. They kept it because it smells like someone\n"
            "  who used to bring them food scraps.\n"
            "  They don't know why."
        ),
        "thought": (
            "  He had children. He had a life. He gave it all away\n"
            "  and nobody was allowed to remember why.\n"
            "\n  [Memory Fragment 4/7 collected]"
        ),
    },
    "frag_5": {
        "room_id": 5,
        "object":  "a hand-carved fishing lure caught in the bridge rope",
        "lore": (
            "  The initials carved into it match no recorded king.\n"
            "  He used to fish here. Before everything.\n"
            "  He was, apparently, not very good at fishing.\n"
            "  The fish here are very old."
        ),
        "thought": (
            "  He was a person. Before he was a king.\n"
            "  Before he was forgotten.\n"
            "\n  [Memory Fragment 5/7 collected]"
        ),
    },
    "frag_6": {
        "room_id": 10,
        "object":  "the nameplate on the final portrait",
        "lore": (
            "  \"He was here. He was real. I will not write the rest.\"\n"
            "  — written by Melos Vane, before he lost himself entirely."
        ),
        "thought": (
            "  Even the archivist couldn't finish erasing him.\n"
            "  There's something in that.\n"
            "\n  [Memory Fragment 6/7 collected]"
        ),
    },
    "frag_7": {
        "room_id": 11,
        "object":  "a child's bootie, stone-grey with age, inside the empty alcove",
        "lore": (
            "  He had a daughter. She was seven when the bargain was made.\n"
            "  She grew up. She had children. None of them knew her father's name.\n"
            "  She left this here, in the space reserved for him,\n"
            "  so he would know someone had come."
        ),
        "thought": (
            "  You think about what it means to leave something\n"
            "  for someone you can't remember.\n"
            "  You think you understand it better than you expected to.\n"
            "\n  [Memory Fragment 7/7 collected]"
        ),
    },
}

FRAGMENT_COMPLETE = (
    "\n  The name assembles itself in your mind from seven broken pieces.\n"
    "  It is a short name. Simple. The kind of name a fisherman might have,\n"
    "  or a soldier, or a father. You say it quietly, just to yourself.\n"
    "  The dungeon goes very still."
)

# ─────────────────────────────────────────────────────────────────────────────
# Journal
# ─────────────────────────────────────────────────────────────────────────────

JOURNAL = [
    {
        "id": "1",
        "title": "Entry 1 — Descent",
        "text": (
            "Descended into the dungeon. Stone walls, torches, the usual.\n"
            "  The air smells wrong — not decay, exactly.\n"
            "  More like something held too long in a closed fist."
        ),
    },
    {
        "id": "2",
        "title": "Entry 2 — First Blood",
        "text": (
            "Killed my first skeleton. It didn't say anything.\n"
            "  I don't know why I expected it to.\n"
            "  I should stop expecting things."
        ),
    },
    {
        "id": "3",
        "title": "Entry 3 — The Mosaic",
        "text": (
            "Found something in the rubble. A mosaic tile.\n"
            "  Someone scratched out the face. Deliberately, carefully,\n"
            "  like they were doing the person a favor.\n"
            "  I don't think they were doing anyone a favor."
        ),
    },
    {
        "id": "4",
        "title": "Entry 4 — Understanding",
        "text": (
            "I think I've been wrong about why I came here.\n"
            "  I came to kill a king. But there's no 'king' here —\n"
            "  there's just a man who was told to forget himself\n"
            "  and did it so completely that now he can't stop."
        ),
    },
    {
        "id": "5",
        "title": "Entry 5 — The Death Knight",
        "text": (
            "Sir Aldric didn't want to die. He didn't want to keep fighting either.\n"
            "  He'd been waiting for someone to relieve him from a post\n"
            "  no one remembered posting him to.\n"
            "  I wonder if 'wanting to stop' and 'not knowing how to'\n"
            "  are different things or the same thing."
        ),
    },
    {
        "id": "6a",
        "title": "Entry 6 — The Name",
        "text": (
            "I know his name. I've known it for a few minutes now\n"
            "  and it already feels like I've always known it.\n"
            "  It's a good name. Simple. The kind of name you give someone\n"
            "  you expect to live a long, quiet life.\n"
            "  I don't think his life was either of those things.\n"
            "  But it's still a good name."
        ),
    },
    {
        "id": "6b",
        "title": "Entry 6 — Almost",
        "text": (
            "There's something I'm missing. Something close.\n"
            "  I can feel it — the way you can feel a word just out of reach.\n"
            "  Maybe I'll find it inside. Maybe I won't."
        ),
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# DEATH lines & epitaphs
# ─────────────────────────────────────────────────────────────────────────────

DEATH_LINES = {
    1:  "BARELY PAST THE THRESHOLD. THAT IS, IN FACT, A RECORD.",
    2:  "KILLED BY A SKELETON. IN AN ARMORY. I APPRECIATE THE POETRY.",
    3:  "THREE GOBLINS. I FEEL IT IS IMPORTANT THAT YOU SIT WITH THAT.",
    4:  "THE DARK MAGE WAS ALSO, IN HIS WAY, A CASUALTY. BUT STILL.",
    5:  "GERALD DIDN'T WANT TO. HE FEELS TERRIBLE. HE HAS GONE BACK TO HIS FISH.",
    6:  "SLAIN IN A TREASURE VAULT. AT LEAST THE SETTING WAS DRAMATIC.",
    7:  "SIR ALDRIC HAS BEEN WAITING FOR PERMISSION TO STOP FIGHTING.\n  YOU DID NOT GIVE IT TO HIM. PERHAPS NEXT TIME.",
    8:  "HE WAS GOING TO REMEMBER SOMETHING. AT THE END.\n  I HEARD THE BEGINNING OF IT. IT STARTED WITH HIS NAME.",
    9:  "THE WARDEN FINALLY FOUND SOMEONE TO ARREST.\n  HE IS, I THINK, RELIEVED.",
    10: "MELOS VANE HAS ADDED YOUR MEMORY TO HIS COLLECTION.\n  YOU WILL BE FORGOTTEN VERY PROFESSIONALLY.",
    11: "THEY DIED LOYAL. THEY ARE STILL LOYAL.\n  THEY HAVE FORGOTTEN WHAT FOR. OLD HABITS.",
    12: "YOU WERE THIS CLOSE. THAT IS NOT ENCOURAGEMENT.\n  IT IS SIMPLY TRUE.",
}

def _get_epitaph(player, room_id):
    name = player.name
    potions = [k for k in player.inventory if ITEMS.get(k) and ITEMS[k].kind == "potion"]
    if room_id == 8:
        if len(player.memories) >= 7:
            return (f"  {name} had all the pieces. {name} ran out of time.\n"
                    "  The name remains unspoken. The King remains angry.")
        return f"  {name} faced the Forgotten King and learned,\n  firsthand, why he is remembered as Forgotten."
    if potions:
        return (f"  {name} died with a Health Potion in their pocket.\n"
                "  It has been left to history to decide whether this was\n"
                "  tragic or simply ironic.")
    if player.level <= 2:
        return (f"  {name} entered the dungeon and discovered, too late,\n"
                "  that confidence is not a substitute for armor.")
    return f"  {name} ventured deep into the Forgotten King's dungeon.\n  The dungeon won."

# ─────────────────────────────────────────────────────────────────────────────
# Enemies
# ─────────────────────────────────────────────────────────────────────────────

class Enemy:
    def __init__(self, name, hp, atk, defense, xp, loot=None, desc="",
                 regen=0, fragment_key=None, special=None):
        self.name         = name
        self.max_hp       = hp
        self.hp           = hp
        self.atk          = atk
        self.defense      = defense
        self.xp           = xp
        self.loot         = loot or []
        self.desc         = desc
        self.regen        = regen
        self.fragment_key = fragment_key
        self.special      = special      # "warden" | "archivist" | None
        self.is_boss      = False
        # combat-state tracking (set fresh on clone)
        self._rounds      = 0

    def alive(self):
        return self.hp > 0

    def take_damage(self, raw):
        actual = max(1, raw - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual

    def do_attack(self):
        self._rounds += 1
        # Warden: immune rounds 1-2 (signaled, handled in run_combat)
        if self.special == "warden" and self._rounds <= 2:
            return ("immune", 0, "")
        # Archivist: monologue rounds 1-2, then normal / forget
        if self.special == "archivist":
            if self._rounds <= 2:
                return ("monologue", self._rounds, "")
            if self.hp <= self.max_hp // 2 and random.random() < 0.35:
                return ("forget", 0, "Ink Erasure")
        dmg = random.randint(self.atk // 2, self.atk)
        # Dark Mage: 30% chance Rotting Bolt (poisons player)
        if self.special == "dark_mage" and random.random() < 0.30:
            return ("poison", dmg, "Rotting Bolt")
        return ("normal", dmg, "")

    def clone(self):
        e = Enemy(self.name, self.max_hp, self.atk, self.defense,
                  self.xp, self.loot[:], self.desc, self.regen,
                  self.fragment_key, self.special)
        e.is_boss = self.is_boss
        return e


class Boss(Enemy):
    """The Forgotten King — two phases, special attack every 3 turns."""

    def __init__(self):
        super().__init__(
            "The Forgotten King", 130, 20, 10, 250,
            [("kings_blade", 1.0), ("mega_potion", 1.0)],
            "A skeletal king on an obsidian throne, eyes burning red.",
        )
        self.is_boss   = True
        self.phase     = 1
        self.sp_timer  = 3

    def do_attack(self):
        if self.hp <= self.max_hp // 2 and self.phase == 1:
            self.phase  = 2
            self.atk   += 8
            return ("phase", 0,
                    "\"Another hero. Another sword. Another face I will forget by morning.\"\n"
                    "\n  He pauses. The red light in his eyes flickers.\n"
                    "\n  \"Do you know what it is to forget your own name?\n"
                    "  I don't. I can't. I remember forgetting it,\n"
                    "  which is somehow worse.\"\n"
                    "\n  Dark energy surges. He enters his FINAL FORM!")
        self.sp_timer -= 1
        if self.sp_timer <= 0:
            self.sp_timer = 3
            dmg = random.randint(28, 38)
            return ("special", dmg, "Death Wave")
        dmg = random.randint(self.atk // 2, self.atk)
        return ("normal", dmg, "")

    def clone(self):
        return Boss()


# Enemy template registry
ENEMIES = {
    "skeleton":    Enemy("Skeleton",      22,  6, 1, 15, [("rusty_dagger", 0.30)],
                         "A rattling undead warrior."),
    # Named goblins for Room 3
    "goblin_skreek": Enemy("Skreek",      16,  5, 0, 12, [("health_potion", 0.25)],
                           "The talky one. Always has opinions about employment models."),
    "goblin_nip":    Enemy("Nip",         16,  5, 0, 12, [("health_potion", 0.25)],
                           "Very concerned about contracts he definitely didn't sign."),
    "goblin_bogrot": Enemy("Bogrot",      16,  5, 0, 12, [("gold_coins", 0.50)],
                           "Currently eating something. Nobody is asking what."),
    "orc":         Enemy("Orc Brute",    40, 11, 3, 32, [("health_potion", 0.40), ("leather_armor", 0.20)],
                         "A massive, roaring green warrior."),
    "dark_mage":   Enemy("Victorinus Fletch",  28, 15, 1, 38,
                         [("strength_potion", 0.35)],
                         "An academic whose identity is fragmenting in real time.",
                         special="dark_mage"),
    "cave_troll":  Enemy("Cave Troll",   60, 13, 5, 50,
                         [("mega_potion", 0.25)],
                         "His name is Gerald. He named himself. He was just living by the river.",
                         regen=6),
    "death_knight":Enemy("Sir Aldric Greymount", 55, 16, 6, 60,
                         [("chain_mail", 0.30), ("skull_key", 0.65)],
                         "An armored champion of death, armor covered in tiny carved letters."),
    # New enemies
    "restless_warden": Enemy("Restless Warden", 35, 10, 2, 28,
                             [("iron_key", 1.0), ("haunted_lantern", 1.0)],
                             "A semi-translucent figure still doing rounds after three centuries.",
                             special="warden"),
    "archivist":   Enemy("Melos Vane, The Archivist", 65, 18, 4, 85,
                         [("ink_black_tome", 1.0), ("mega_potion", 1.0)],
                         "A lich who has been erasing history for 300 years.",
                         fragment_key="frag_6", special="archivist"),
    "cursed_carath":  Enemy("Lord Carath",  50, 14, 8, 45,
                            [("plate_armor", 0.40)],
                            "He died protecting the name of a man he loved like a father. He has forgotten the name."),
    "cursed_steward": Enemy("The Unnamed Steward", 50, 14, 8, 45,
                            [],
                            "No name on his tomb. Some people are forgotten before they die.",
                            fragment_key="frag_7"),
}

# ─────────────────────────────────────────────────────────────────────────────
# Player
# ─────────────────────────────────────────────────────────────────────────────

XP_TABLE = [0, 0, 80, 200, 380, 620, 940, 1350, 1870, 2520]

class Player:
    def __init__(self, name):
        self.name          = name
        self.level         = 1
        self.xp            = 0
        self.max_hp        = 55
        self.hp            = 55
        self.base_atk      = 8
        self.base_def      = 2
        self.weapon_key    = "rusty_dagger"
        self.armor_key     = None
        self.inventory     = []
        self.gold          = 0
        self.kills         = 0
        self.str_boost     = 0
        self.str_boost_t   = 0
        # New v2 attributes
        self.memories      = []     # list of frag keys collected
        self.wagers_used   = 0      # DEATH wager uses (max 2)
        self.poison_turns  = 0      # turns of 4-dmg/turn poison
        self.curse_turns   = 0      # turns of ??? ATK display
        self.weary_combats = 0      # remaining combats with -3 DEF
        self.journal_flags = set()  # unlocked journal entry IDs
        self.last_death_room = None

    @property
    def weapon(self):
        return ITEMS[self.weapon_key]

    @property
    def armor(self):
        return ITEMS[self.armor_key] if self.armor_key else None

    @property
    def atk(self):
        return self.base_atk + self.weapon.value + self.str_boost

    @property
    def defense(self):
        base = self.base_def + (self.armor.value if self.armor else 0)
        if self.weary_combats > 0:
            base = max(0, base - 3)
        return base

    def alive(self):
        return self.hp > 0

    def do_attack(self):
        raw  = random.randint(self.atk // 2, self.atk)
        crit = random.random() < 0.10
        if crit:
            raw = int(raw * 1.75)
        return raw, crit

    def heal(self, amount):
        gained = min(amount, self.max_hp - self.hp)
        self.hp += gained
        return gained

    def take_damage(self, raw, defending=False):
        mult = 2 if defending else 1
        actual = max(1, raw - self.defense * mult)
        self.hp = max(0, self.hp - actual)
        return actual

    def gain_xp(self, amount):
        self.xp += amount
        levelled = []
        while self.level < len(XP_TABLE) - 1 and self.xp >= XP_TABLE[self.level + 1]:
            self.level  += 1
            hp_g  = random.randint(8, 14)
            atk_g = random.randint(1, 3)
            def_g = random.randint(0, 2)
            self.max_hp   += hp_g
            self.hp        = min(self.max_hp, self.hp + hp_g)
            self.base_atk += atk_g
            self.base_def += def_g
            levelled.append((self.level, hp_g, atk_g, def_g))
        return levelled

    def xp_to_next(self):
        if self.level >= len(XP_TABLE) - 1:
            return 0
        return XP_TABLE[self.level + 1] - self.xp

    def tick_buffs(self):
        if self.str_boost_t > 0:
            self.str_boost_t -= 1
            if self.str_boost_t == 0:
                self.str_boost = 0
        if self.curse_turns > 0:
            self.curse_turns -= 1

    def has(self, key):
        return key in self.inventory

    def add_item(self, key):
        if len(self.inventory) < 10:
            self.inventory.append(key)
            return True
        return False

    def equip(self, key):
        item = ITEMS.get(key)
        if not item or key not in self.inventory:
            return False
        if item.kind == "weapon":
            if self.weapon_key != "rusty_dagger":
                self.inventory.append(self.weapon_key)
            self.weapon_key = key
            self.inventory.remove(key)
            return True
        elif item.kind == "armor":
            if self.armor_key:
                self.inventory.append(self.armor_key)
            self.armor_key = key
            self.inventory.remove(key)
            return True
        return False

    def use_potion(self, key):
        item = ITEMS.get(key)
        if not item or item.kind != "potion" or key not in self.inventory:
            return None
        self.inventory.remove(key)
        if item.effect == "str_boost":
            self.str_boost   = item.value
            self.str_boost_t = 5
            return f"ATK +{item.value} for 5 turns!"
        healed = self.heal(item.value)
        # Potion also cures poison
        if self.poison_turns > 0:
            self.poison_turns = 0
            return f"Restored {healed} HP. Poison cured!"
        return f"Restored {healed} HP."

    def hp_bar(self, width=22):
        pct    = self.hp / self.max_hp
        filled = int(width * pct)
        col    = C.GREEN if pct > 0.6 else (C.YELLOW if pct > 0.3 else C.RED)
        bar    = colored("█" * filled + "░" * (width - filled), col)
        return f"{bar} {self.hp}/{self.max_hp}"


# ─────────────────────────────────────────────────────────────────────────────
# Rooms / Map
# ─────────────────────────────────────────────────────────────────────────────

class Room:
    def __init__(self, rid, name, desc, exits=None, enemies=None,
                 items=None, locked=False, key=None, lore=None,
                 fragment_key=None, examine_lore=None):
        self.rid          = rid
        self.name         = name
        self.desc         = desc
        self.exits        = exits        or {}
        self._enemies     = enemies      or []
        self.items        = items        or []
        self.locked       = locked
        self.key          = key
        self.lore         = lore
        self.fragment_key = fragment_key  # memory fragment discoverable here
        self.examine_lore = examine_lore  # extra lore on examine (no fragment)
        self.visited      = False
        self.cleared      = False
        self.taken        = set()
        self.fragment_taken = False

    def live_enemies(self):
        if self.cleared:
            return []
        return [ENEMIES[k].clone() for k in self._enemies]

    def available_items(self):
        return [k for k in self.items if k not in self.taken]


def build_map():
    return {
        1: Room(1, "Dungeon Entrance",
                "Mossy stone steps descend into torchlit darkness. The stench of rot\n"
                "  hangs in the damp air. Cracked walls sweat cold water. No going back.",
                exits={"north": 3, "east": 2},
                items=["health_potion"],
                fragment_key="frag_1",
                examine_lore="You notice a cracked mosaic tile in the wall. "
                             "Something about it feels deliberate."),

        2: Room(2, "Armory",
                "Rusted racks line the walls — most gear is beyond salvage, but a\n"
                "  few pieces survive. Skeletons of dead soldiers slump in the corners.",
                exits={"west": 1, "north": 4},
                enemies=["skeleton", "skeleton"],
                items=["short_sword", "leather_armor"],
                fragment_key="frag_2",
                examine_lore="Dusty shelves. Something glints near the back — "
                             "a commendation medal, face-down."),

        3: Room(3, "Goblin Den",
                "The floor is filth and bones. Small green figures dart between\n"
                "  overturned crates, hissing at each other — and at you.",
                exits={"south": 1, "north": 5, "east": 4, "west": 9},
                enemies=["goblin_skreek", "goblin_nip", "goblin_bogrot"],
                items=["health_potion", "iron_key"],
                fragment_key="frag_4",
                examine_lore="Goblins have no use for paper, but they kept this scrap "
                             "wedged under a crate. Something about it stops you."),

        4: Room(4, "Dark Library",
                "Towering shelves reach a vaulted ceiling. Most tomes are ash.\n"
                "  A single candle gutters over a legible page.",
                exits={"south": 3, "west": 2, "east": 6, "north": 7},
                enemies=["dark_mage"],
                items=["strength_potion"],
                lore="'To face the King, bring the Skull Key. To survive — bring courage.'",
                fragment_key="frag_3",
                examine_lore="A half-burned letter on the reading table. "
                             "Someone tried to write something important."),

        5: Room(5, "Underground River",
                "A black river slices through the rock floor, cold and utterly silent.\n"
                "  Something enormous stirs beneath the surface.",
                exits={"south": 3, "east": 7},
                enemies=["cave_troll"],
                items=["chain_mail", "mega_potion"],
                fragment_key="frag_5",
                examine_lore="Something is caught in the bridge rope — a small carved object."),

        6: Room(6, "Treasure Vault",
                "Gold glitters behind iron bars. One cage stands open — someone\n"
                "  left in a hurry. The wealth of a kingdom, left to rot.",
                exits={"west": 4},
                enemies=["orc", "orc"],
                items=["battle_axe", "health_potion", "gold_coins"],
                locked=True, key="iron_key"),

        7: Room(7, "Guard Barracks",
                "Rows of long-abandoned bunks. Tattered war banners hang from the\n"
                "  rafters. The King's elite guard never got their orders to stand down.",
                exits={"south": 5, "west": 4, "north": 12},
                enemies=["death_knight"],
                items=["plate_armor"]),

        8: Room(8, "Throne Room",
                "An enormous chamber of black stone. An obsidian throne dominates the\n"
                "  far wall. Atop it sits a figure in tattered royal robes, crown askew,\n"
                "  empty sockets burning red. It turns its head — slowly — toward you.",
                exits={"south": 12},
                locked=True, key="skull_key"),

        # ── New rooms ──────────────────────────────────────────────────────
        9: Room(9, "The Prison Cells",
                "Iron bars line both walls. Most cells hold nothing but old bones\n"
                "  and older regrets. One cell still has a tattered blanket.\n"
                "  A lantern swings, lit, though there is nobody left to light it.",
                exits={"east": 3, "north": 10},
                enemies=["restless_warden"],
                items=["haunted_lantern"],
                examine_lore=(
                    "  In one cell, scratch marks count the days. The last tally\n"
                    "  trails off mid-stroke. You count them.\n"
                    "  124,098.\n"
                    "  That's 340 years. Someone stopped counting.\n"
                    "  You prefer not to think about why."
                )),

        10: Room(10, "The Portrait Gallery",
                "A long hall of portraits. Every face has been methodically scratched\n"
                "  out — not vandalized, erased. The golden frames remain, the fine\n"
                "  clothes remain, the painted hands remain. But where the faces were:\n"
                "  raw stone. Someone did this carefully. Over a very long time.",
                exits={"south": 9, "east": 11},
                enemies=["archivist"],
                fragment_key="frag_6",
                examine_lore=(
                    "  On the final portrait, the face is scratched out, but someone\n"
                    "  has written in the plaque below:\n"
                    "  \"He was here. He was real. I will not write the rest.\""
                )),

        11: Room(11, "The Royal Crypt",
                "Stone sarcophagi line the walls, carved with names and dates —\n"
                "  the King's family, his court, his heirs. Their names are intact.\n"
                "  Only one alcove is empty: a space clearly prepared, with a\n"
                "  name-plate that reads simply '_______'.",
                exits={"west": 10, "east": 12},
                enemies=["cursed_carath", "cursed_steward"],
                items=["kings_crown"],
                fragment_key="frag_7",
                examine_lore=(
                    "  The empty alcove reads: \"Reserved for the one who will not be named.\"\n"
                    "  Someone left a space for him. Someone expected him to have a name when he died."
                )),

        12: Room(12, "The Throne Antechamber",
                "The air is different here — colder, stiller, like the world\n"
                "  holding its breath. The great doors ahead are sealed with\n"
                "  skull-shaped locks. Torches burn blue.",
                exits={"south": 7, "north": 8},
                items=["final_letter"],
                examine_lore=(
                    "  On the wall, someone has written in what might be charcoal:\n"
                    "  'Turn back. He has been waiting a very long time.\n"
                    "  He is very angry. Also, he used to be kind.'\n"
                    "  The handwriting is shaky. Old."
                )),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Combat helpers
# ─────────────────────────────────────────────────────────────────────────────

def enemy_hp_bar(enemy, width=16):
    pct    = enemy.hp / enemy.max_hp
    filled = int(width * pct)
    col    = C.RED if pct > 0.35 else C.YELLOW
    return colored("█" * filled + "░" * (width - filled), col)


def _grant_fragment(player, frag_key):
    """Add a fragment to player.memories and display its text. Returns True if new."""
    if frag_key in player.memories:
        return False
    player.memories.append(frag_key)
    frag = MEMORY_FRAGMENTS[frag_key]
    print()
    print(colored(f"  ✦ {frag['object'].upper()}", C.MAGENTA, C.BOLD))
    print()
    for line in frag["lore"].split("\n"):
        slow_print(colored(line, C.WHITE), delay=0.018)
    print()
    for line in frag["thought"].split("\n"):
        slow_print(colored(line, C.DIM), delay=0.015)
    if len(player.memories) == 7:
        print()
        slow_print(colored(FRAGMENT_COMPLETE, C.YELLOW, C.BOLD), delay=0.018)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Combat
# ─────────────────────────────────────────────────────────────────────────────

def run_combat(player, enemies, room_name, room_id=None):
    """
    Turn-based combat.
    Returns: "victory" | "dead" | "fled" | "true_ending" | "peaceful"
    """
    # ── Inspired buff: fragment already collected in this room ──────────────
    inspired_atk = 0
    if room_id and room_id in [MEMORY_FRAGMENTS[k]["room_id"] for k in player.memories]:
        # Check specifically if the fragment from this room is already in memories
        for fk, fd in MEMORY_FRAGMENTS.items():
            if fd["room_id"] == room_id and fk in player.memories:
                inspired_atk = 5
                break

    # ── Pre-combat speak checks (before loop) ───────────────────────────────
    # Warden: speak if 2+ memories
    if any(e.special == "warden" for e in enemies) and len(player.memories) >= 2:
        clear()
        print(colored(f"\n  ⚔  ENCOUNTER — {room_name}  ⚔\n", C.CYAN, C.BOLD))
        slow_print(colored(
            "\n  The Warden stops. He looks at you for a very long time.\n"
            "  For three centuries he has had a job to do and nobody to do it to.\n"
            "  You represent, in some sense, the fulfillment of his entire existence.\n"
            "  He seems confused about how he feels about that.\n", C.DIM), delay=0.016)
        print(colored("  You sense he might respond to reason.\n", C.CYAN))
        print(colored("  [You have 2+ Memories — you understand something of his purpose]", C.MAGENTA))
        print()
        ch = input(colored("  Speak to the Warden? (y/n): ", C.CYAN)).strip().lower()
        if ch == "y":
            slow_print(colored(
                "\n  You speak — not commands, not threats. Something else.\n"
                "  You talk about the King. About what you've found.\n"
                "  About what it means to keep doing a job when the person\n"
                "  who gave it to you has been erased from all record.\n", C.WHITE), delay=0.016)
            slow_print(colored(
                "\n  The Warden goes very still.\n"
                "  Then, slowly, he sets down his lantern.\n"
                "  He looks at his hands. He looks at the lantern.\n"
                "  He begins to fade.\n", C.DIM), delay=0.016)
            slow_print(colored(
                "\n  You get the feeling that 'relieved' is the right word\n"
                "  for what he is feeling, even if 'feeling' is generous.\n", C.DIM), delay=0.016)
            total_xp = sum(e.xp for e in enemies)
            levelled = player.gain_xp(total_xp)
            player.kills += len(enemies)
            print(colored(f"\n  +{total_xp} XP (peaceful resolution)", C.GREEN))
            for lv, hp_g, atk_g, def_g in levelled:
                print(colored(f"\n  ★ LEVEL UP! You are now Level {lv}! ★", C.YELLOW, C.BOLD))
                print(colored(f"    Max HP +{hp_g}  |  ATK +{atk_g}  |  DEF +{def_g}", C.YELLOW))
            # Warden drops haunted_lantern peacefully
            if "haunted_lantern" not in player.inventory and len(player.inventory) < 10:
                player.add_item("haunted_lantern")
                print(colored("  The lantern remains. You take it.", C.YELLOW))
            pause()
            return "peaceful"
        # Player chose not to speak — proceed to combat

    # Gerald: speak if 4+ memories (Room 5 only)
    if room_id == 5 and any(e.name == "Cave Troll" for e in enemies) and len(player.memories) >= 4:
        clear()
        print(colored(f"\n  ⚔  ENCOUNTER — {room_name}  ⚔\n", C.CYAN, C.BOLD))
        slow_print(colored(
            "\n  The Cave Troll stops. He looks at you. He looks at his fish.\n"
            "  He looks at you again.\n"
            "\n  He makes a sound like a very large, very sad accordion.\n"
            "\n  This is, you will later learn, the trollish word for:\n"
            "  \"I genuinely did not want things to go this way.\"\n", C.DIM), delay=0.016)
        print(colored("  [You have 4+ Memories — you understand something about this place]", C.MAGENTA))
        print()
        ch = input(colored("  Try to speak with him? (y/n): ", C.CYAN)).strip().lower()
        if ch == "y":
            slow_print(colored(
                "\n  What follows is a very slow, very broken conversation.\n"
                "  Gerald knows things. He was here. He witnessed it —\n"
                "  the night of the bargain, three hundred years ago.\n"
                "  He watched from the river. He has been waiting for someone\n"
                "  who would understand what he saw.\n", C.WHITE), delay=0.016)
            slow_print(colored(
                "\n  He gives you something. Something small.\n"
                "  He also gives you a fish.\n"
                "  The fish does nothing. It is simply a fish.\n"
                "  Gerald feels it is important that you have it.\n", C.DIM), delay=0.016)
            total_xp = sum(e.xp for e in enemies)
            levelled = player.gain_xp(total_xp)
            player.kills += len(enemies)
            print(colored(f"\n  +{total_xp} XP (peaceful resolution)", C.GREEN))
            for lv, hp_g, atk_g, def_g in levelled:
                print(colored(f"\n  ★ LEVEL UP! You are now Level {lv}! ★", C.YELLOW, C.BOLD))
                print(colored(f"    Max HP +{hp_g}  |  ATK +{atk_g}  |  DEF +{def_g}", C.YELLOW))
            _grant_fragment(player, "frag_5")
            if "geralds_fish" not in player.inventory and len(player.inventory) < 10:
                player.add_item("geralds_fish")
                print(colored("  Gerald's Fish added to inventory.", C.YELLOW))
            pause()
            return "peaceful"

    # ── Main combat loop ─────────────────────────────────────────────────────
    clear()
    print(colored(f"\n  ⚔  COMBAT — {room_name}  ⚔\n", C.RED, C.BOLD))
    if inspired_atk:
        print(colored("  [INSPIRED] The memory steels your resolve. ATK +5 this combat.\n", C.MAGENTA))

    round_num = 0
    while player.alive() and any(e.alive() for e in enemies):
        alive = [e for e in enemies if e.alive()]
        round_num += 1

        # ── Poison damage at round start ────────────────────────────────────
        if player.poison_turns > 0:
            poison_dmg = 4
            player.hp = max(0, player.hp - poison_dmg)
            player.poison_turns -= 1
            print(colored(f"\n  POISON deals {poison_dmg} damage! [{player.poison_turns} turns remaining]", C.GREEN))
            if not player.alive():
                break

        # ── Draw combat state ────────────────────────────────────────────────
        print(hr())
        print(colored(f"  Round {round_num}", C.DIM))
        # Status effects
        statuses = []
        if player.poison_turns > 0:
            statuses.append(colored(f"[POISONED-{player.poison_turns}]", C.GREEN))
        if player.curse_turns > 0:
            statuses.append(colored(f"[CURSED-{player.curse_turns}]", C.MAGENTA))
        if player.weary_combats > 0:
            statuses.append(colored("[WEARY]", C.DIM))
        if inspired_atk:
            statuses.append(colored("[INSPIRED]", C.MAGENTA))
        if statuses:
            print("  " + "  ".join(statuses))
        print()
        print(colored("  Enemies:", C.RED))
        for i, e in enumerate(alive):
            bar = enemy_hp_bar(e)
            immune_tag = ""
            if e.special == "warden" and e._rounds < 2:
                immune_tag = colored("  [PROCESSING]", C.CYAN)
            print(f"    {i+1}. {colored(e.name, C.RED, C.BOLD)}  "
                  f"{bar}  {e.hp}/{e.max_hp} HP{immune_tag}")
        print()
        atk_display = "???" if player.curse_turns > 0 else str(player.atk + inspired_atk)
        print(f"  {colored('You:', C.CYAN, C.BOLD)} {player.hp_bar()}"
              f"  ATK {colored(atk_display, C.RED)}  DEF {colored(player.defense, C.BLUE)}")
        if player.str_boost:
            print(colored(f"  [BUFFED] ATK +{player.str_boost} ({player.str_boost_t} turns)", C.MAGENTA))
        print()

        # ── Choose target ────────────────────────────────────────────────────
        target = alive[0]
        if len(alive) > 1:
            print(colored("  Target:", C.CYAN))
            for i, e in enumerate(alive):
                print(f"    {i+1}. {e.name}")
            while True:
                ch = input(colored("  > ", C.CYAN)).strip()
                if ch.isdigit() and 1 <= int(ch) <= len(alive):
                    target = alive[int(ch) - 1]
                    break

        # ── Determine speak availability ─────────────────────────────────────
        can_speak = False
        speak_reason = ""
        if isinstance(target, Boss) or any(isinstance(e, Boss) for e in alive):
            if len(player.memories) >= 7:
                can_speak = True
                speak_reason = "Speak his name  [requires all 7 Memories]"
        # (Warden/Gerald speak already handled pre-loop)

        # ── Player action ────────────────────────────────────────────────────
        action_line = "  Actions:  1) Attack  2) Use Potion  3) Defend  4) Flee"
        if can_speak:
            action_line += "  5) " + speak_reason
        print(colored(action_line, C.CYAN))
        defending = False
        acted     = False
        while not acted:
            choice = input(colored("  > ", C.CYAN)).strip().lower()

            if choice == "1":
                raw, crit = player.do_attack()
                raw += inspired_atk
                dmg = target.take_damage(raw)
                # Warden immunity: half damage first 2 rounds
                if target.special == "warden" and round_num <= 2:
                    dmg = max(1, dmg // 2)
                    target.hp = max(0, target.hp + dmg)  # undo and redo
                    actual_dmg = target.take_damage(raw // 2)
                    dmg = actual_dmg
                    print(colored(f"\n  Your strike passes halfway through the Warden...\n"
                                  f"  {dmg} damage (reduced — he hasn't fully materialized).", C.DIM))
                elif crit:
                    print(colored(f"\n  CRITICAL HIT! You strike {target.name} for {dmg} damage!", C.YELLOW, C.BOLD))
                else:
                    print(colored(f"\n  You strike {target.name} for {dmg} damage.", C.WHITE))
                # King's Blade lifesteal
                if player.weapon.effect == "lifesteal":
                    stolen = max(1, dmg // 4)
                    player.heal(stolen)
                    print(colored(f"  King's Blade siphons {stolen} HP!", C.MAGENTA))
                acted = True

            elif choice == "2":
                potions = [(i, k) for i, k in enumerate(player.inventory)
                           if ITEMS[k].kind == "potion"]
                if not potions:
                    print(colored("  No potions!", C.RED))
                    continue
                for _, k in potions:
                    idx = player.inventory.index(k) + 1
                    it  = ITEMS[k]
                    print(f"    {idx}. {colored(it.name, C.GREEN)} — {it.desc}")
                while True:
                    sel = input(colored("  Use #: ", C.CYAN)).strip()
                    if sel.isdigit() and 1 <= int(sel) <= len(player.inventory):
                        k = player.inventory[int(sel) - 1]
                        if ITEMS[k].kind == "potion":
                            result = player.use_potion(k)
                            print(colored(f"\n  {result}", C.GREEN))
                            acted = True
                            break
                    print(colored("  Invalid.", C.RED))

            elif choice == "3":
                defending = True
                print(colored("\n  You brace for impact...", C.BLUE))
                acted = True

            elif choice == "4":
                if random.random() < 0.40:
                    print(colored("\n  You dash for the exit!", C.YELLOW))
                    pause()
                    return "fled"
                print(colored("\n  You couldn't escape!", C.RED))
                acted = True

            elif choice == "5" and can_speak:
                # True Ending: speak the King's name
                return "true_ending"

            else:
                print(colored("  Unknown command.", C.DIM))

        # ── Goblin surrender check (Room 3) ──────────────────────────────────
        alive_now = [e for e in enemies if e.alive()]
        if room_id == 3 and len(alive_now) == 1 and alive_now[0].hp <= 4:
            last = alive_now[0]
            print()
            slow_print(colored(
                f'  {last.name} throws down their weapon and backs away.\n'
                f'\n  "Alright, alright! I yield! The iron key\'s in the big crate,\n'
                f'  second from the left! Don\'t tell Bogrot I told you!"\n'
                f'\n  They flee into the shadows.\n', C.YELLOW), delay=0.016)
            total_xp = sum(e.xp for e in enemies)
            levelled = player.gain_xp(total_xp)
            player.kills += len([e for e in enemies if not e.alive()]) + 1
            print(colored(f"  +{total_xp} XP", C.GREEN))
            for lv, hp_g, atk_g, def_g in levelled:
                print(colored(f"\n  ★ LEVEL UP! Level {lv}! ★", C.YELLOW, C.BOLD))
                print(colored(f"    Max HP +{hp_g}  |  ATK +{atk_g}  |  DEF +{def_g}", C.YELLOW))
            pause()
            return "victory"

        # ── Enemy turns ──────────────────────────────────────────────────────
        for e in [x for x in enemies if x.alive()]:
            if not player.alive():
                break

            # Troll regeneration
            if e.regen and e.alive():
                regen = min(e.regen, e.max_hp - e.hp)
                if regen:
                    e.hp += regen
                    print(colored(f"\n  {e.name} regenerates {regen} HP!", C.MAGENTA))

            if not e.alive():
                continue

            if e.is_boss:
                result = e.do_attack()
                kind, raw_dmg, msg = result
                if kind == "phase":
                    print()
                    for line in msg.split("\n"):
                        slow_print(colored(f"  {line}", C.RED, C.BOLD), delay=0.018)
                    continue
                elif kind == "special":
                    actual = player.take_damage(raw_dmg, defending)
                    print(colored(f"\n  {e.name} unleashes {colored(msg, C.BOLD, C.RED)} "
                                  f"— {actual} damage!", C.RED))
                else:
                    actual = player.take_damage(raw_dmg, defending)
                    print(colored(f"\n  {e.name} strikes for {actual} damage.", C.RED))

            else:
                result = e.do_attack()
                kind, raw_dmg, msg = result

                if kind == "immune":
                    print(colored(f"\n  The Warden is still processing your presence...", C.DIM))

                elif kind == "monologue":
                    if raw_dmg == 1:
                        slow_print(colored(
                            "\n  Melos Vane sets down his erasing tool and regards you\n"
                            "  with the weary patience of someone who has seen adventurers before.\n"
                            "\n  \"You are here,\" he says, \"because you believe memory matters.\n"
                            "  I understand. I used to believe the same thing.\n"
                            "  I have since learned that memory is simply suffering\n"
                            "  with better filing.\"", C.DIM), delay=0.014)
                    else:
                        slow_print(colored(
                            "\n  \"The mercy of forgetting,\" Melos Vane continues,\n"
                            "  as though you are not trying to kill him,\n"
                            "  \"is underrated. Consider: everything you remember\n"
                            "  that causes you pain — gone. Every regret — erased.\n"
                            "  I am offering you a gift. You simply cannot see it yet.\"\n"
                            "\n  He picks up his erasing tool again.\n"
                            "  He seems entirely sincere.\n"
                            "  This is, somehow, worse.", C.DIM), delay=0.014)

                elif kind == "forget":
                    player.curse_turns = 2
                    slow_print(colored(
                        f"\n  {e.name} performs Ink Erasure!\n"
                        "  You feel your grip on yourself slip, briefly.\n"
                        "  You can't quite remember your own strength.\n"
                        "  [CURSED — ATK displays as ??? for 2 turns]", C.MAGENTA), delay=0.015)

                elif kind == "poison":
                    actual = player.take_damage(raw_dmg, defending)
                    player.poison_turns = 4
                    print(colored(f"\n  {e.name} unleashes {colored(msg, C.BOLD, C.GREEN)}!\n"
                                  f"  {actual} damage + POISONED (4 damage/turn, 4 turns)!", C.GREEN))

                else:  # normal
                    actual = player.take_damage(raw_dmg, defending)
                    print(colored(f"\n  {e.name} attacks for {actual} damage.", C.RED))

        player.tick_buffs()

        if not player.alive():
            break

        alive = [e for e in enemies if e.alive()]
        if alive:
            pause("  [Enter for next round]")
            clear()
            print(colored(f"\n  ⚔  COMBAT — {room_name}  ⚔\n", C.RED, C.BOLD))
            if inspired_atk:
                print(colored("  [INSPIRED] ATK +5\n", C.MAGENTA))

    # ── Outcome ───────────────────────────────────────────────────────────────
    if not player.alive():
        return "dead"

    print(colored("\n  Victory! All enemies defeated.\n", C.GREEN, C.BOLD))

    # Decrement weary
    if player.weary_combats > 0:
        player.weary_combats -= 1

    # XP
    total_xp = sum(e.xp for e in enemies)
    levelled  = player.gain_xp(total_xp)
    player.kills += len(enemies)
    print(colored(f"  +{total_xp} XP", C.GREEN))

    for lv, hp_g, atk_g, def_g in levelled:
        print()
        print(colored(f"  ★ LEVEL UP! You are now Level {lv}! ★", C.YELLOW, C.BOLD))
        print(colored(f"    Max HP +{hp_g}  |  ATK +{atk_g}  |  DEF +{def_g}", C.YELLOW))

    # Fragment drops from enemies
    for e in enemies:
        if e.fragment_key and e.fragment_key not in player.memories:
            print()
            _grant_fragment(player, e.fragment_key)

    # Regular loot drops
    drops = []
    for e in enemies:
        for key, chance in e.loot:
            if random.random() < chance:
                drops.append((key, e.name))

    if drops:
        print(colored("\n  Loot:", C.YELLOW))
        for key, src in drops:
            item = ITEMS[key]
            col  = ITEM_COLOR.get(item.kind, C.WHITE)
            if item.kind == "misc" and key == "gold_coins":
                player.gold += item.value
                print(f"    • {colored(item.name, col)} (+{item.value}g) from {src}")
            elif len(player.inventory) < 10:
                auto = False
                if item.kind == "weapon" and item.value > ITEMS[player.weapon_key].value:
                    player.add_item(key)
                    player.equip(key)
                    print(f"    • {colored(item.name, col)} (auto-equipped!) from {src}")
                    auto = True
                elif item.kind == "armor" and (
                        not player.armor_key or item.value > ITEMS[player.armor_key].value):
                    player.add_item(key)
                    player.equip(key)
                    print(f"    • {colored(item.name, col)} (auto-equipped!) from {src}")
                    auto = True
                if not auto:
                    player.add_item(key)
                    print(f"    • {colored(item.name, col)} → inventory from {src}")
            else:
                print(colored(f"    • {item.name} from {src} — inventory full, lost!", C.RED))

    pause()
    return "victory"


# ─────────────────────────────────────────────────────────────────────────────
# Display helpers
# ─────────────────────────────────────────────────────────────────────────────

MAP_ART = """
  ┌──────────────────────────────────────────────────────────────┐
  │                   [8] Throne Room  ★                         │
  │                         │  ↑ skull key                       │
  │                  [12] Antechamber                            │
  │     [11] Royal Crypt ───┤                                    │
  │          │          [7] Guard Barracks                       │
  │   [10] Portrait         │              ↑                     │
  │       Gallery      [5] River    [4] Dark Library ── [6] Vault│
  │          │               └─────────────┤                     │
  │   [9] Prison Cells   [3] Goblin Den ───┘    ↑ iron key       │
  │          └──────────────┤                                    │
  │                   [1] Entrance ── [2] Armory                 │
  └──────────────────────────────────────────────────────────────┘
"""

def show_map(current_id):
    print(colored(MAP_ART, C.DIM))
    print(colored(f"  You are in: Room {current_id}", C.CYAN))
    print()


def show_stats(player):
    print(hr())
    lv_str   = colored(f"Level {player.level}", C.CYAN, C.BOLD)
    xp_str   = colored(f"{player.xp} XP (+{player.xp_to_next()} to next)", C.GREEN)
    gold_str = colored(f"{player.gold}g", C.YELLOW)
    kill_str = colored(f"{player.kills} kills", C.RED)
    mem_str  = colored(f"Memories: {len(player.memories)}/7", C.MAGENTA)
    print(f"  {colored(player.name, C.WHITE, C.BOLD)}  │  {lv_str}  │  {xp_str}  │  {gold_str}  │  {kill_str}")
    print(f"  HP: {player.hp_bar()}")
    print(f"  ATK {colored(player.atk, C.RED)}  DEF {colored(player.defense, C.BLUE)}  "
          f"Weapon: {colored(player.weapon.name, C.YELLOW)}  "
          f"Armor: {colored(player.armor.name if player.armor else 'None', C.YELLOW)}  "
          f"{mem_str}")
    if player.str_boost:
        print(colored(f"  [BUFFED] ATK +{player.str_boost} ({player.str_boost_t} turns)", C.MAGENTA))
    if player.poison_turns > 0:
        print(colored(f"  [POISONED — {player.poison_turns} turns remaining]", C.GREEN))
    print(hr())


def show_inventory(player):
    print(colored("\n  ══ INVENTORY ══", C.CYAN, C.BOLD))
    if not player.inventory:
        print(colored("  (empty)", C.DIM))
    else:
        for i, key in enumerate(player.inventory):
            item = ITEMS[key]
            col  = ITEM_COLOR.get(item.kind, C.WHITE)
            eqp  = ""
            if key == player.weapon_key or key == player.armor_key:
                eqp = colored(" [equipped]", C.DIM)
            print(f"    {colored(i+1, C.BOLD)}. {colored(item.name, col)}{eqp} — {colored(item.desc, C.DIM)}")
    print(f"  Slots: {len(player.inventory)}/10  │  Gold: {colored(player.gold, C.YELLOW)}g")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Game
# ─────────────────────────────────────────────────────────────────────────────

class Game:
    def __init__(self):
        self.player      = None
        self.rooms       = build_map()
        self.room_id     = 1
        self.over        = False
        self.won         = False
        self.true_ending = False

    def room(self):
        return self.rooms[self.room_id]

    # ── main loop ─────────────────────────────────────────────────────────────
    def run(self):
        self._title_screen()
        # Unlock journal entry 1 at start
        self.player.journal_flags.add("1")
        while not self.over:
            self._room_loop()
        if self.won:
            if self.true_ending:
                self._screen_true_ending()
            else:
                self._screen_victory()

    def _title_screen(self):
        clear()
        print(colored(r"""
  ██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗
  ██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║
  ██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║
  ██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║
  ██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║
  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
         of the  F O R G O T T E N   K I N G
""", C.YELLOW, C.BOLD))
        print(colored("  A dungeon of combat, memory, and the cost of being forgotten\n", C.DIM))
        name = input(colored("  Enter your hero's name: ", C.CYAN)).strip()
        self.player = Player(name or "Hero")
        clear()
        slow_print(colored(f"\n  Welcome, {self.player.name}. The dungeon awaits...\n", C.YELLOW))
        slow_print(colored(
            "  You stand at the entrance of the Forgotten King's dungeon.\n"
            "  Somewhere deep within, something waits.\n"
            "  Kill it, or understand it.\n"
            "  Both are options.\n", C.DIM))
        pause()

    # ── room display & commands ────────────────────────────────────────────────
    def _room_loop(self):
        room = self.room()
        clear()
        dungeon_ascii_art.print_room_art(self.room_id)
        print(colored(f"\n  ═══ {room.name.upper()} ═══", C.CYAN, C.BOLD))
        print()
        print(colored(f"  {room.desc}", C.WHITE))
        print()

        # Lore on first visit
        if room.lore and not room.visited:
            print(colored(f"  📖 {room.lore}", C.MAGENTA))
            print()

        # Room 12 special message (all 7 fragments)
        if self.room_id == 12 and not room.visited:
            if len(self.player.memories) >= 7:
                print(colored(
                    "  The name is on the tip of your tongue.\n"
                    "  It has always been there.\n", C.YELLOW, C.BOLD))
            self._unlock_journal_room12()

        room.visited = True

        # Enemies present?
        enemies = room.live_enemies()
        if enemies:
            print(colored("  Enemies:", C.RED))
            for e in enemies:
                print(f"    • {colored(e.name, C.RED, C.BOLD)} — {colored(e.desc, C.DIM)}")
            print()

        # Items on floor?
        floor_items = room.available_items()
        if floor_items:
            print(colored("  Items:", C.YELLOW))
            for key in floor_items:
                it  = ITEMS[key]
                col = ITEM_COLOR.get(it.kind, C.WHITE)
                print(f"    • {colored(it.name, col)} — {colored(it.desc, C.DIM)}")
            print()

        # Fragment hint?
        if room.fragment_key and room.fragment_key not in self.player.memories and not room.fragment_taken:
            print(colored("  Something here catches your eye. [x] to examine.", C.DIM))
            print()

        # Exits
        print(colored("  Exits:", C.GREEN))
        for direction, dest_id in room.exits.items():
            dest     = self.rooms[dest_id]
            lock_tag = colored(" [LOCKED]", C.RED) if dest.locked else ""
            print(f"    {colored(direction.upper(), C.GREEN, C.BOLD)}: {dest.name}{lock_tag}")
        print()

        show_stats(self.player)
        print(colored("  Commands: [n/s/e/w] move  [f] fight  [t] take  "
                      "[x] examine  [j] journal  [i] inventory  [m] map  [?] help", C.DIM))
        print()
        cmd = input(colored("  > ", C.CYAN)).strip().lower()

        if cmd in ("n", "s", "e", "w", "north", "south", "east", "west"):
            dirs = {"n": "north", "s": "south", "e": "east", "w": "west"}
            self._move(dirs.get(cmd, cmd))

        elif cmd in ("f", "fight"):
            self._fight(room, enemies)

        elif cmd in ("t", "take", "pickup"):
            self._take(room)

        elif cmd in ("x", "examine", "look"):
            self._examine(room)

        elif cmd in ("j", "journal"):
            self._show_journal()

        elif cmd in ("i", "inv", "inventory"):
            self._inventory_menu()

        elif cmd in ("m", "map"):
            clear()
            show_map(self.room_id)
            pause()

        elif cmd in ("?", "h", "help"):
            self._help()

        elif cmd in ("q", "quit"):
            if input(colored("  Quit? (y/n): ", C.RED)).strip().lower() == "y":
                print(colored("\n  The dungeon claims another soul...\n", C.DIM))
                sys.exit(0)

        else:
            print(colored("  Unknown command. Type [?] for help.", C.DIM))
            pause()

    # ── move ──────────────────────────────────────────────────────────────────
    def _move(self, direction):
        room = self.room()
        if room.live_enemies() and not room.cleared:
            print(colored("\n  Enemies block the exit! Fight them first.", C.RED))
            pause()
            return
        if direction not in room.exits:
            print(colored(f"\n  You can't go {direction} from here.", C.DIM))
            pause()
            return
        dest_id = room.exits[direction]
        dest    = self.rooms[dest_id]
        if dest.locked:
            if dest.key and self.player.has(dest.key):
                key_name = ITEMS[dest.key].name
                print(colored(f"\n  You use the {key_name} to unlock the door!", C.YELLOW))
                dest.locked = False
                self.player.inventory.remove(dest.key)
                pause()
            else:
                need = ITEMS[dest.key].name if dest.key else "a key"
                print(colored(f"\n  Locked. You need: {need}.", C.RED))
                pause()
                return
        self.room_id = dest_id
        slow_print(colored(f"\n  You move {direction}...", C.DIM), delay=0.018)

    # ── fight ─────────────────────────────────────────────────────────────────
    def _fight(self, room, enemies):
        if room.cleared or not enemies:
            print(colored("\n  No enemies here.", C.DIM))
            pause()
            return

        # ── Pre-combat intros ────────────────────────────────────────────────
        self._show_combat_intro(room, enemies)

        # Build combat enemies
        if self.room_id == 8:
            combat_enemies = [Boss()]
        else:
            combat_enemies = enemies

        result = run_combat(self.player, combat_enemies, room.name, self.room_id)

        if result in ("victory", "peaceful"):
            room.cleared = True
            # Post-combat special messages
            self._show_post_combat(room)
            # Journal updates
            if self.room_id == 7:
                self.player.journal_flags.add("5")
            if self.player.kills == 1 and "2" not in self.player.journal_flags:
                self.player.journal_flags.add("2")
            if self.room_id == 8:
                self.over = True
                self.won  = True

        elif result == "true_ending":
            room.cleared = True
            self.over        = True
            self.won         = True
            self.true_ending = True

        elif result == "dead":
            self.player.last_death_room = self.room_id
            self._handle_death()

    def _show_combat_intro(self, room, enemies):
        """Show pre-combat intro text before entering run_combat."""
        rid = self.room_id
        clear()

        if rid == 3:
            # Goblin banter
            print(colored(f"\n  ═══ {room.name.upper()} ═══\n", C.RED, C.BOLD))
            slow_print(colored(
                '  Skreek:  "I\'m just saying, attacking every adventurer is not\n'
                '           a sustainable employment model."\n'
                '  Nip:     "We don\'t have a choice. It\'s in the contract."\n'
                '  Skreek:  "We never signed a contract."\n'
                '  Nip:     "That\'s not relevant."\n'
                '  Bogrot:  [eating something]\n'
                '  Skreek:  "What IS he eating?"\n'
                '  Nip:     "Don\'t ask."\n', C.DIM), delay=0.014)
            slow_print(colored(
                '           ... [they notice you] ...\n'
                '\n'
                '  Skreek:  "Oh. Another one."\n'
                '  Nip:     "Kill it."\n'
                '  Bogrot:  [still eating]\n', C.DIM), delay=0.014)
            pause("  [Press Enter to fight]")
            return

        if rid == 5:
            # Gerald
            print(colored(f"\n  ═══ {room.name.upper()} ═══\n", C.RED, C.BOLD))
            slow_print(colored(
                "  The Cave Troll stops. He looks at you. He looks at his fish.\n"
                "  He looks at you again.\n"
                "\n  He makes a sound like a very large, very sad accordion.\n"
                "\n  This is, you will later learn, the trollish word for:\n"
                "  \"I genuinely did not want things to go this way.\"\n"
                "\n  Then he charges.\n", C.DIM), delay=0.016)
            pause("  [Press Enter to fight]")
            return

        if rid == 7:
            # Sir Aldric Greymount
            print(colored(f"\n  ═══ {room.name.upper()} ═══\n", C.RED, C.BOLD))
            slow_print(colored(
                "  The Death Knight does not charge. He stands very still.\n"
                "\n  \"Adventurer.\" His voice is the sound of rusted hinges\n"
                "  on a door that leads nowhere.\n"
                "\n  \"I do not wish to fight you.\"\n"
                "\n  A pause. Long enough to be geological.\n"
                "\n  \"I have not wished to fight anyone for approximately three\n"
                "  centuries. Nevertheless.\"\n"
                "\n  He raises his sword.\n"
                "\n  \"If you kill me — and you might — look at my armor.\n"
                "  The letters. I have been trying to remember something.\n"
                "  Perhaps you will do better.\"\n"
                "\n  Then he attacks.\n", C.DIM), delay=0.016)
            pause("  [Press Enter to fight]")
            return

        if rid == 4:
            # Dark Mage (Victorinus Fletch)
            print(colored(f"\n  ═══ {room.name.upper()} ═══\n", C.RED, C.BOLD))
            slow_print(colored(
                "  \"Fletch — that is, I — that is, he — entered the dungeon\n"
                "  for academic purposes in the autumn of last year.\n"
                "  Or possibly forty years ago. Time is somewhat —\"\n"
                "\n  He gestures. Dark lightning crackles between his fingers.\n"
                "\n  \"— Professor Fletch would like to note that he retains\n"
                "  some control over —\"\n"
                "\n  He looks at his hands. They are doing something\n"
                "  he didn't ask them to do.\n"
                "\n  \"— ah.\"\n"
                "\n  He looks genuinely apologetic.\n"
                "  \"I am sorry for what is about to happen.\"\n", C.DIM), delay=0.016)
            pause("  [Press Enter to fight]")
            return

        if rid == 9:
            # Restless Warden
            print(colored(f"\n  ═══ {room.name.upper()} ═══\n", C.RED, C.BOLD))
            slow_print(colored(
                "  The Warden walks toward you with the purposeful stride of\n"
                "  someone who has an important job to do.\n"
                "\n  His rounds haven't changed in three centuries.\n"
                "  You are the first person he's actually found to arrest.\n"
                "  He seems relieved, in the way that only the very lost\n"
                "  can seem relieved.\n", C.DIM), delay=0.016)
            pause("  [Press Enter]")
            return

        if rid == 10:
            # Archivist
            print(colored(f"\n  ═══ {room.name.upper()} ═══\n", C.RED, C.BOLD))
            slow_print(colored(
                "  Melos Vane looks up from the portrait he is carefully destroying.\n"
                "  He has been destroying portraits for 300 years.\n"
                "  He is very good at it.\n"
                "\n  He regards you with the weary patience of someone who has\n"
                "  seen adventurers before. They always ask questions.\n"
                "  They always die having learned the wrong answers.\n", C.DIM), delay=0.016)
            pause("  [Press Enter to fight]")
            return

        if rid == 11:
            # Cursed Ancestors
            print(colored(f"\n  ═══ {room.name.upper()} ═══\n", C.RED, C.BOLD))
            slow_print(colored(
                "  Lord Carath died protecting the name of a man he loved\n"
                "  like a father. He has forgotten the name now.\n"
                "  He has forgotten why he is still standing.\n"
                "  He has not forgotten how to swing a sword.\n"
                "  Some muscle memories are very deep.\n"
                "\n  The steward next to him has no name on his tomb.\n"
                "  Some people are forgotten before they die.\n"
                "  He seems to have made his peace with it. Mostly.\n", C.DIM), delay=0.016)
            pause("  [Press Enter to fight]")
            return

        if rid == 8:
            # The Forgotten King
            print(colored(f"\n  ═══ {room.name.upper()} ═══\n", C.RED, C.BOLD))
            slow_print(colored(
                "  The figure on the throne does not move.\n"
                "\n  Then — slowly, with the creak of something that has been\n"
                "  still for a very long time — it turns its head toward you.\n"
                "\n  The red light in its eye sockets regards you.\n"
                "\n  It says nothing.\n"
                "\n  It has been saying nothing for three hundred years.\n"
                "\n  You raise your weapon.\n", C.DIM), delay=0.016)
            if len(self.player.memories) >= 7:
                slow_print(colored(
                    "\n  [You carry all 7 Memories. You know his name.\n"
                    "  During combat, you may choose to SPEAK it.]\n", C.MAGENTA), delay=0.014)
            pause("  [Press Enter to fight]")
            return

    def _show_post_combat(self, room):
        """Post-combat flavor for specific rooms."""
        rid = self.room_id
        if rid == 4:
            print()
            slow_print(colored(
                "  Victorinus Fletch — Professor Fletch — whatever he was at the end —\n"
                "  slumps to the floor. The dark energy dissipates.\n"
                "  He looks, briefly, like himself again.\n"
                "\n  \"I remembered,\" he says, to no one in particular.\n"
                "  \"I had a cat. Her name was...\"\n"
                "\n  He does not finish the sentence.\n", C.DIM), delay=0.016)
            pause()
        elif rid == 7:
            print()
            slow_print(colored(
                "  You examine Sir Aldric's armor. Thousands of tiny carved letters.\n"
                "  Partial names. Half-words. Phonetic attempts.\n"
                "  None of them are right.\n"
                "\n  One section, near his heart, has been carved deeper than the rest.\n"
                "  Seven letters. They are almost right.\n"
                "\n  You feel the name pulling at you, like a word on the tip of your tongue.\n", C.DIM), delay=0.016)
            # If this is the 6th fragment, hint the 7th
            if len(self.player.memories) == 6:
                slow_print(colored(
                    "  Six pieces. You have a feeling the last one is nearby.\n", C.MAGENTA), delay=0.016)
            pause()

    # ── take items ────────────────────────────────────────────────────────────
    def _take(self, room):
        available = room.available_items()
        if not available:
            print(colored("\n  Nothing to take here.", C.DIM))
            pause()
            return

        if len(available) == 1:
            self._pick_up(room, available[0])
            pause()
            return

        print(colored("\n  What will you take?", C.CYAN))
        for i, key in enumerate(available):
            it  = ITEMS[key]
            col = ITEM_COLOR.get(it.kind, C.WHITE)
            print(f"    {i+1}. {colored(it.name, col)} — {colored(it.desc, C.DIM)}")
        print("    0. Take all   c. Cancel")

        ch = input(colored("  > ", C.CYAN)).strip().lower()
        if ch == "0":
            for key in available:
                self._pick_up(room, key, silent=False)
        elif ch.isdigit() and 1 <= int(ch) <= len(available):
            self._pick_up(room, available[int(ch) - 1])
        elif ch == "c":
            return
        pause()

    def _pick_up(self, room, key, silent=False):
        item = ITEMS[key]
        if item.kind == "misc" and key == "gold_coins":
            room.taken.add(key)
            self.player.gold += item.value
            if not silent:
                print(colored(f"\n  Picked up {item.name} (+{item.value}g)!", C.YELLOW))
            return
        if len(self.player.inventory) >= 10:
            print(colored(f"\n  Inventory full — can't take {item.name}!", C.RED))
            return
        room.taken.add(key)
        self.player.add_item(key)
        col = ITEM_COLOR.get(item.kind, C.WHITE)
        if not silent:
            print(colored(f"\n  Picked up {colored(item.name, col)}.", C.WHITE))
        # Final letter triggers journal
        if key == "final_letter":
            self._unlock_journal_room12()
            print(colored(
                "\n  The letter describes a man who carved the warning on the wall.\n"
                "  He was the last custodian of the dungeon before the King went silent.\n"
                "  He knew the name. He couldn't write it.\n"
                "  He left anyway, because some things you can only carry for so long.\n", C.DIM))
        if item.kind in ("weapon", "armor"):
            better = (item.kind == "weapon" and item.value > ITEMS[self.player.weapon_key].value) or \
                     (item.kind == "armor"  and (not self.player.armor_key or
                      item.value > ITEMS[self.player.armor_key].value))
            prompt = f"  Equip {item.name}?"
            if better:
                prompt += " (UPGRADE)"
            ch = input(colored(f"{prompt} (y/n): ", C.CYAN)).strip().lower()
            if ch == "y":
                self.player.equip(key)
                print(colored(f"  {item.name} equipped!", C.GREEN))

    # ── examine ───────────────────────────────────────────────────────────────
    def _examine(self, room):
        clear()
        print(colored(f"\n  ═══ EXAMINE — {room.name.upper()} ═══\n", C.CYAN, C.BOLD))

        found_something = False

        # Fragment discovery
        if room.fragment_key and room.fragment_key not in self.player.memories and not room.fragment_taken:
            frag = MEMORY_FRAGMENTS[room.fragment_key]
            slow_print(colored(f"  You notice: {frag['object']}.\n", C.WHITE))
            room.fragment_taken = True
            found_something = True
            _grant_fragment(self.player, room.fragment_key)
            # Journal unlocks
            if "3" not in self.player.journal_flags:
                self.player.journal_flags.add("3")
            if len(self.player.memories) >= 4 and "4" not in self.player.journal_flags:
                self.player.journal_flags.add("4")

        elif room.fragment_key and room.fragment_key in self.player.memories:
            frag = MEMORY_FRAGMENTS[room.fragment_key]
            print(colored(f"  [You've already examined: {frag['object']}]\n", C.DIM))
            found_something = True

        # Room-specific examine lore
        if room.examine_lore:
            if not found_something:
                found_something = True
            print()
            for line in room.examine_lore.split("\n"):
                slow_print(colored(line, C.DIM), delay=0.016)

        if not found_something:
            print(colored("  You examine the room carefully. Nothing notable catches your eye.", C.DIM))

        pause()

    # ── journal ───────────────────────────────────────────────────────────────
    def _show_journal(self):
        clear()
        print(colored("\n  ══ JOURNAL ══\n", C.CYAN, C.BOLD))
        shown = 0
        for entry in JOURNAL:
            if entry["id"] in self.player.journal_flags:
                shown += 1
                print(colored(f"  ─── {entry['title']} ───", C.YELLOW))
                for line in entry["text"].split("\n"):
                    print(colored(f"  {line}", C.WHITE))
                print()
        if not shown:
            print(colored("  (Nothing written yet.)", C.DIM))
        pause()

    def _unlock_journal_room12(self):
        """Unlock journal entry 6 when entering/examining Room 12."""
        if "6a" not in self.player.journal_flags and "6b" not in self.player.journal_flags:
            if len(self.player.memories) >= 7:
                self.player.journal_flags.add("6a")
            else:
                self.player.journal_flags.add("6b")

    # ── inventory menu ────────────────────────────────────────────────────────
    def _inventory_menu(self):
        clear()
        show_inventory(self.player)
        print(colored("  1. Use/Equip item  2. Drop item  3. Back", C.CYAN))
        ch = input(colored("  > ", C.CYAN)).strip()

        if ch == "1":
            if not self.player.inventory:
                print(colored("  Nothing to use.", C.DIM)); pause(); return
            idx = input(colored("  Item # to use/equip: ", C.CYAN)).strip()
            if idx.isdigit() and 1 <= int(idx) <= len(self.player.inventory):
                key  = self.player.inventory[int(idx) - 1]
                item = ITEMS[key]
                if item.kind == "potion":
                    res = self.player.use_potion(key)
                    print(colored(f"\n  {res}", C.GREEN))
                elif item.kind in ("weapon", "armor"):
                    self.player.equip(key)
                    print(colored(f"\n  {item.name} equipped!", C.GREEN))
                elif item.kind == "key":
                    print(colored(f"\n  Use the {item.name} at a locked door.", C.YELLOW))
                else:
                    print(colored(f"\n  {item.desc}", C.DIM))
            pause()

        elif ch == "2":
            if not self.player.inventory:
                print(colored("  Nothing to drop.", C.DIM)); pause(); return
            idx = input(colored("  Drop item #: ", C.CYAN)).strip()
            if idx.isdigit() and 1 <= int(idx) <= len(self.player.inventory):
                key = self.player.inventory.pop(int(idx) - 1)
                print(colored(f"\n  Dropped {ITEMS[key].name}.", C.DIM))
            pause()

    # ── help ──────────────────────────────────────────────────────────────────
    def _help(self):
        clear()
        print(colored("\n  ══ HELP ══\n", C.CYAN, C.BOLD))
        print("  Movement    n / s / e / w  (or full word)")
        print("  Fight       f              engage enemies")
        print("  Take        t              pick up items")
        print("  Examine     x              search room for lore & memories")
        print("  Journal     j              read collected journal entries")
        print("  Inventory   i              manage items")
        print("  Map         m              show dungeon map")
        print("  Quit        q\n")
        print(colored("  Combat options:", C.YELLOW))
        print("  1. Attack  — strike target (10% crit for 1.75× damage)")
        print("  2. Potion  — use a potion (also cures poison)")
        print("  3. Defend  — doubles DEF this round")
        print("  4. Flee    — 40% chance to escape")
        print("  5. Speak   — context-sensitive: appears with Warden (2+ Memories),")
        print("               Gerald (4+ Memories), or the King (all 7 Memories)\n")
        print(colored("  Memories:", C.MAGENTA))
        print("  Examine rooms to find Memory Fragments — 7 total.")
        print("  Collecting all 7 unlocks a hidden ending.\n")
        print(colored("  Status effects:", C.GREEN))
        print("  POISONED  — 4 damage/turn; cured by any potion")
        print("  CURSED    — ATK displays as ??? for 2 turns (ATK still works)")
        print("  WEARY     — DEF -3 for 2 combats after DEATH wager")
        print("  INSPIRED  — ATK +5 if you examined a fragment here before fighting\n")
        print(colored("  Tips:", C.GREEN))
        print("  • New rooms: west of Goblins, then further north and east")
        print("  • The Throne Room is now reached through the Antechamber")
        print("  • Death Knight drops the Skull Key for the Throne Room\n")
        pause()

    # ── DEATH wager ───────────────────────────────────────────────────────────
    def _handle_death(self):
        p = self.player
        room_id = p.last_death_room or self.room_id

        clear()
        print(colored("""
  D E A T H
""", C.DIM, C.BOLD))

        death_line = DEATH_LINES.get(room_id, "YOU ARE DEAD. THIS IS THE PART I AM CERTAIN ABOUT.")
        slow_print(colored(f"  A TALL FIGURE STEPS FROM THE SHADOWS.\n", C.DIM), delay=0.02)
        print()
        for line in death_line.split("\n"):
            slow_print(colored(f"  {line}", C.WHITE, C.BOLD), delay=0.02)
        print()

        if p.wagers_used < 2:
            # Offer wager
            slow_print(colored(
                "\n  WELL. I HAVE BEEN EXPECTING THIS VISIT.\n"
                "  NOT QUITE SO SOON. BUT. HERE WE ARE.\n"
                "\n  I HAVE A PROPOSITION. I AM WILLING TO RETURN YOU\n"
                "  TO THE LAND OF THE LIVING IN EXCHANGE FOR —\n", C.WHITE, C.BOLD), delay=0.018)

            # Choose what DEATH wants
            payment_options = []
            non_key_items = [k for k in p.inventory
                             if ITEMS[k].kind not in ("key",) and k not in ("final_letter",)]
            if non_key_items:
                payment_options.append(("item", random.choice(non_key_items)))
            if p.xp > 20:
                payment_options.append(("xp", max(10, p.xp // 5)))
            if p.memories:
                payment_options.append(("fragment", random.choice(p.memories)))

            if not payment_options:
                payment_options.append(("xp", 5))

            weights = {"item": 60, "xp": 30, "fragment": 10}
            wager_type, wager_val = random.choices(
                payment_options,
                weights=[weights.get(o[0], 30) for o in payment_options]
            )[0]

            if wager_type == "item":
                item_name = ITEMS[wager_val].name
                slow_print(colored(f"  — {item_name.upper()}\n", C.YELLOW, C.BOLD), delay=0.02)
            elif wager_type == "xp":
                slow_print(colored(f"  — {wager_val} EXPERIENCE POINTS\n", C.YELLOW, C.BOLD), delay=0.02)
            else:
                frag = MEMORY_FRAGMENTS.get(wager_val, {})
                obj  = frag.get("object", "a Memory Fragment")
                slow_print(colored(f"  — ONE OF YOUR MEMORIES ({obj})\n", C.YELLOW, C.BOLD), delay=0.02)

            slow_print(colored(
                "\n  I WANT TO BE CLEAR THAT I DO NOT NEED ANY OF THESE THINGS.\n"
                "  I HAVE EVERYTHING. I AM SIMPLY CURIOUS WHETHER\n"
                "  YOU WANT TO LIVE MORE THAN YOU WANT TO KEEP THEM.\n", C.WHITE, C.BOLD), delay=0.018)

            if p.wagers_used == 1:
                slow_print(colored(
                    "  TWICE. YOU ARE EITHER VERY BRAVE OR VERY BAD AT STAYING ALIVE.\n"
                    "  THESE ARE NOT MUTUALLY EXCLUSIVE.\n", C.DIM), delay=0.018)

            print()
            ch = input(colored("  Accept the wager? (y/n): ", C.CYAN)).strip().lower()

            if ch == "y":
                # Apply payment
                if wager_type == "item":
                    if wager_val in p.inventory:
                        p.inventory.remove(wager_val)
                    elif wager_val == p.weapon_key:
                        p.weapon_key = "rusty_dagger"
                    elif wager_val == p.armor_key:
                        p.armor_key = None
                    print(colored(f"\n  DEATH takes {ITEMS[wager_val].name}.", C.DIM))
                elif wager_type == "xp":
                    p.xp = max(0, p.xp - wager_val)
                    print(colored(f"\n  DEATH takes {wager_val} XP.", C.DIM))
                else:
                    if wager_val in p.memories:
                        p.memories.remove(wager_val)
                    frag = MEMORY_FRAGMENTS.get(wager_val, {})
                    print(colored(f"\n  DEATH takes a Memory. You can still feel the shape of it,\n"
                                  "  like a word you've forgotten. Just the shape.", C.DIM))

                p.wagers_used += 1
                p.weary_combats = 2
                p.hp = max(1, p.max_hp // 2)
                p.poison_turns = 0
                p.curse_turns  = 0

                slow_print(colored(
                    "\n  DEATH fades.\n"
                    "  You are alive, but the border left its mark.\n"
                    "  [WEARY — DEF -3 for your next 2 combats]\n", C.DIM), delay=0.018)
                pause()
                return  # Player survives — game continues

            else:
                # Refused
                slow_print(colored(
                    "\n  SENSIBLE. MOST PEOPLE CANNOT RESIST THE OFFER.\n"
                    "  IT SPEAKS WELL OF YOUR CHARACTER.\n"
                    f"  GOODBYE, {p.name.upper()}.\n", C.WHITE, C.BOLD), delay=0.018)
                pause()

        self.over = True
        self._screen_death()

    # ── end screens ───────────────────────────────────────────────────────────
    def _screen_death(self):
        clear()
        print(colored("""
  ██╗   ██╗ ██████╗ ██╗   ██╗    ██████╗ ██╗███████╗██████╗
  ╚██╗ ██╔╝██╔═══██╗██║   ██║    ██╔══██╗██║██╔════╝██╔══██╗
   ╚████╔╝ ██║   ██║██║   ██║    ██║  ██║██║█████╗  ██║  ██║
    ╚██╔╝  ██║   ██║██║   ██║    ██║  ██║██║██╔══╝  ██║  ██║
     ██║   ╚██████╔╝╚██████╔╝    ██████╔╝██║███████╗██████╔╝
     ╚═╝    ╚═════╝  ╚═════╝     ╚═════╝ ╚═╝╚══════╝╚═════╝
""", C.RED, C.BOLD))
        p = self.player
        epitaph = _get_epitaph(p, p.last_death_room or self.room_id)
        print()
        for line in epitaph.split("\n"):
            slow_print(colored(line, C.DIM), delay=0.018)
        print()
        print(colored(f"  Level {p.level}  │  {p.kills} kills  │  {p.xp} XP  │  {p.gold}g  │  Memories: {len(p.memories)}/7", C.WHITE))
        print()

    def _screen_victory(self):
        """The Sword Ending."""
        clear()
        print(colored("""
  ██╗   ██╗██╗ ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗██╗
  ██║   ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝██║
  ██║   ██║██║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝ ██║
  ╚██╗ ██╔╝██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝  ╚═╝
   ╚████╔╝ ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║   ██╗
    ╚═══╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝
""", C.YELLOW, C.BOLD))

        slow_print(colored(
            "  The Forgotten King crumbles to ash.\n"
            "\n  The red light fades. The throne room goes cold.\n", C.WHITE), delay=0.018)
        pause("  [Press Enter]")
        print()
        slow_print(colored("  A tall figure steps from the shadows.\n", C.DIM), delay=0.018)
        print()
        slow_print(colored(
            "  DEATH: WELL. THAT'S THAT, THEN.\n"
            "\n         I HAVE BEEN WAITING FOR SOMEONE TO COME FOR A\n"
            "         VERY LONG TIME. I WANT YOU TO KNOW THAT I AM\n"
            "         NOT UNGRATEFUL.\n"
            "\n         [pause]\n"
            "\n         HE WAS GOING TO SAY SOMETHING. AT THE END.\n"
            "         I HEARD THE BEGINNING OF IT. I THINK IT STARTED\n"
            "         WITH HIS NAME.\n"
            "\n         [pause]\n"
            "\n         HE IS AT PEACE NOW. EVENTUALLY, EVERYTHING IS.\n"
            "         IT JUST TAKES SOME PEOPLE LONGER THAN OTHERS.\n", C.WHITE, C.BOLD), delay=0.014)
        print()
        slow_print(colored(
            "  DEATH fades.\n"
            "  The dungeon is very quiet.\n"
            "  The Forgotten King's name dies with him.\n"
            "  Nobody will ever know it now.\n", C.DIM), delay=0.018)
        print()
        print(colored("                    YOU WIN.", C.YELLOW, C.BOLD))
        print(colored("          (This is, apparently, what winning feels like.)\n", C.DIM))
        p = self.player
        print(colored(f"  ── Final Stats: {p.name} ──", C.CYAN))
        print(f"    Level    {p.level}")
        print(f"    XP       {p.xp}")
        print(f"    Kills    {p.kills}")
        print(f"    Gold     {p.gold}g")
        print(f"    Memories {len(p.memories)}/7")
        if len(p.memories) < 7:
            print(colored("    (7/7 Memories unlocks the True Ending)", C.DIM))
        print()

    def _screen_true_ending(self):
        """The True Ending — you spoke his name."""
        clear()
        p = self.player
        print(colored("\n  ═══ THE THRONE ROOM ═══\n", C.CYAN, C.BOLD))

        slow_print(colored(
            "  You say the name.\n"
            "\n  It hangs in the air like smoke.\n", C.WHITE), delay=0.02)
        pause("  [Press Enter]")
        print()
        slow_print(colored(
            "  The King goes completely still.\n"
            "\n  The red light in his eye sockets dims — not to nothing,\n"
            "  but to something warmer. Something that might have been,\n"
            "  long ago, a candle.\n", C.DIM), delay=0.018)
        pause("  [Press Enter]")
        print()
        slow_print(colored(
            "  \"...oh.\"\n"
            "\n  A very long silence.\n"
            "\n  \"Someone remembered.\"\n"
            "\n  [pause]\n"
            "\n  \"It was you. You're the one. After all this time—\"\n", C.WHITE), delay=0.018)
        pause("  [Press Enter]")
        print()
        slow_print(colored(
            "  He looks at his hands. At the throne. At the dungeon\n"
            "  he has haunted for three centuries.\n"
            "\n  \"I'm so tired.\"\n", C.DIM), delay=0.018)
        pause("  [Press Enter]")
        print()
        slow_print(colored(
            "  \"Leave. Please. I would like to be alone with myself\n"
            "  for a few minutes. I haven't been alone with myself\n"
            "  in a very long time.\"\n", C.WHITE), delay=0.018)
        pause("  [Press Enter]")
        print()
        slow_print(colored(
            "  You turn to go.\n"
            "\n  Behind you, quietly, you hear him say his own name.\n"
            "  Just once.\n"
            "  Just to hear how it sounds.\n"
            "\n  You do not look back.\n", C.DIM), delay=0.02)
        pause("  [Press Enter]")

        clear()
        print(colored("""
             R E M E M B E R E D
""", C.YELLOW, C.BOLD))
        slow_print(colored(
            "  The Forgotten King remembered his name.\n"
            "  The binding broke. The curse lifted.\n"
            "  Somewhere in the dungeon, a portrait's scratched-out\n"
            "  face briefly became clear — just for a moment —\n"
            "  then faded again.\n"
            "\n  But it had been there. It had been real.\n"
            "\n  That, it turns out, was enough.\n", C.WHITE), delay=0.018)
        print()
        pause("  [Press Enter]")
        print()
        slow_print(colored(
            "  DEATH, one final time:\n"
            "\n  \"I HAVE SEEN A GREAT MANY ENDINGS.\n"
            "  THIS IS NOT THE WORST ONE.\n"
            "  THAT IS, FROM ME, EXTREMELY HIGH PRAISE.\"\n", C.WHITE, C.BOLD), delay=0.016)
        print()
        print(colored(f"  ── Final Stats: {p.name} ──", C.CYAN))
        print(f"    Level    {p.level}")
        print(f"    XP       {p.xp}")
        print(f"    Kills    {p.kills}")
        print(f"    Gold     {p.gold}g")
        print(colored(f"    Memories {len(p.memories)}/7  ✦  TRUE ENDING", C.YELLOW, C.BOLD))
        print()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    try:
        Game().run()
    except KeyboardInterrupt:
        print(colored("\n\n  Interrupted. Farewell, brave adventurer.\n", C.DIM))
        sys.exit(0)


if __name__ == "__main__":
    main()
