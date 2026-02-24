# Dungeon of the Forgotten King

A text-based Python dungeon crawler about combat, memory, and the cost of being forgotten.

```
  ██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗
  ██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║
  ██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║
  ██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║
  ██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║
  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
         of the  F O R G O T T E N   K I N G
```

## The Story

The King had a name. He made a bargain — sacrifice his name, his identity, his place in all memory — to bind a demon that would have destroyed the kingdom. The kingdom was saved. His name was erased from every record, every portrait, every gravestone.

He sits on his throne, cursed to wait until someone *truly remembers* him.

Centuries of forgetting have curdled his grief into rage.

There are two ways this ends.

## Play in the Browser

```bash
pip3 install flask flask-sock
python3 server.py
```

Then open **http://localhost:5000** in any browser. Works on phones too — open the URL from any device on your network using your machine's local IP (shown on startup).

Uses xterm.js + WebSockets + a real PTY under the hood. Every color, animation, and ASCII art panel renders exactly as intended.

## Play in the Terminal

Python 3.7+. No dependencies.

```bash
python3 dungeon_game.py
```

ANSI color support required (all modern terminals qualify). For phone play via terminal, SSH in with [Termius](https://termius.com/) or similar.

## The Dungeon (12 Rooms)

```
                   [8] Throne Room  ★
                         │  ↑ skull key
                  [12] Antechamber
     [11] Royal Crypt ───┤
          │          [7] Guard Barracks
   [10] Portrait         │
       Gallery      [5] River    [4] Dark Library ── [6] Vault
          │               └─────────────┤                ↑ iron key
   [9] Prison Cells   [3] Goblin Den ───┘
          └──────────────┤
                   [1] Entrance ── [2] Armory
```

Each room has hand-crafted ASCII art and a named cast of characters.

## Characters

| Character | Room | Notes |
|---|---|---|
| Skreek, Nip & Bogrot | Goblin Den | Bicker their way into every fight. Surrender if cornered. |
| Victorinus Fletch | Dark Library | Academic. Identity fragmenting. Genuinely apologetic about the lightning. |
| Gerald | Underground River | His name is Gerald. He named himself. He was just living by the river. |
| Sir Aldric Greymount | Guard Barracks | 340 years trying to remember something. His armor is covered in carved attempts. |
| Restless Warden | Prison Cells | Still doing rounds. First person he's found to arrest in three centuries. |
| Melos Vane, The Archivist | Portrait Gallery | Has been erasing history for 300 years. Very thorough. Very sad. |
| Lord Carath & The Unnamed Steward | Royal Crypt | Died loyal. Still loyal. Forgotten what for. |
| The Forgotten King | Throne Room | The boss. Also the victim. Also the point. |
| DEATH | Everywhere | Dry wit. Fair. Will negotiate. |

## Commands

### Exploration
| Command | Action |
|---|---|
| `n` / `s` / `e` / `w` | Move between rooms |
| `f` | Fight enemies |
| `t` | Take items |
| `x` | Examine — search the room for Memory Fragments and lore |
| `j` | Journal — read collected entries |
| `i` | Inventory |
| `m` | Map |
| `?` | Help |

### Combat
| Input | Action |
|---|---|
| `1` | Attack |
| `2` | Use potion (also cures poison) |
| `3` | Defend — doubles DEF this round |
| `4` | Flee — 40% chance |
| `5` | **Speak** — context-sensitive; appears with certain enemies when conditions are met |

## Memory Fragments

Seven fragments are hidden across the dungeon, found by typing `x` to examine a room. Each reveals a piece of the King's history.

Collect all seven and something changes in the Throne Room.

## Status Effects

- **Poisoned** — 4 damage per turn; cured by any potion
- **Cursed** — ATK displays as `???` for 2 turns (it still works; it's psychological)
- **Inspired** — ATK +5 when you've examined a fragment in the current room before fighting
- **Weary** — DEF -3 for 2 combats; the price DEATH charges for a second chance

## DEATH

If you die, DEATH appears. Twice per run, he'll offer to return you to life in exchange for something — an item, some XP, or a Memory. You can refuse. He finds refusal admirable.

The third time, there's no offer.

## Two Endings

There is the ending where you kill the King.

There is the other one.

The journal will tell you which direction you're going.

## Tips

- Examine every room — fragments are easy to miss
- Goblins talk before they fight; listen carefully
- The Death Knight doesn't want to be there either
- Cave Trolls regenerate HP each round — burst them down fast
- The Archivist won't attack for the first two rounds; he's making a point
- The Restless Warden becomes something else if you know enough
- Gerald will give you a fish. Keep the fish.
