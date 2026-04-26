# FLStaticPatch
Config-based tool that applies patches to binary files.

See the following snippet for an example config file:
```
#Format:
#Filename SHA-1 hash. Base: Origin.
#Offset: Data type Original value -> New value = Explanation.(*) ~Author
#* means the edit is applied by the installer, rather than the file being patched directly.
#
Common.dll 54975b712f85957bc497c4159406a72413605b14. Base: Default from the official 1.1 Freelancer patch.
0638AC: Hex 7B -> EB = Removes the maximum docking initiation distance. ~BC46
0E698E: Hex 7C -> EB = Allows many planets to continue spinning. ~adoxa
18D210: Int32 -1 -> 1001 = Skips the first-time machine speed test and assume the highest speed for determining default performance options. ~BC46

Content.dll 54975b712f85957bc497c4159406a72413605b14. Base: Default from the official 1.1 Freelancer patch.
037068: Hex 02 -> 03 = Fixes NPCs saying the first number of their call sign twice when requesting to dock. ~BC46

Freelancer.exe 54975b712f85957bc497c4159406a72413605b14. Base: Default No-CD EXE.
06A440: Int8 80 -> 127 = Increases the maximum number of characters in the chat input box. ~M0tah
075A56: UInt32 1125 -> 1102 = Changes the ids_info of player waypoints to a non-uppercased string ("PLAYER WAYPOINT" -> "Player Waypoint"). ~BC46
085D5D: Float32 0.089 -> 0.13 = Increases the clickable area width of the load-save menu buttons (after loading a game) such that the property matches with all other menu-style buttons. ~BC46
```

A `#` character at the start of the line means this line is commented out (ignored).
