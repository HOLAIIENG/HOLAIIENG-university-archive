# 场景道具模型 / Scene Prop Models

跑酷新场景（草地 / 海上城市）使用的真实 3D 模型，全部为 **CC0（公共领域）** 授权，作者 **Quaternius**，来源 [Poly Pizza](https://poly.pizza/u/Quaternius)。CC0 可自由用于个人与商业项目，无需署名（此处署名仅为致谢）。

| 文件 | 模型 | 来源 | 授权 |
|------|------|------|------|
| `tree.glb` | Tree | https://poly.pizza/m/qZtx0AHhcy | CC0 |
| `pine_tree.glb` | Pine Tree | https://poly.pizza/m/gX8WmgkeEm | CC0 |
| `business_building.glb` | Business Building | https://poly.pizza/m/GoF3zph6WI | CC0 |
| `house.glb` | House | https://poly.pizza/m/vZ1CLbWmSx | CC0 |
| `town_center.glb` | Town Center | https://poly.pizza/m/CoERW5nFdE | CC0 |
| `road_kit.glb` | Modular Road Kit（取 `road_square` 片平铺为道路）| https://poly.pizza/m/YClppstaHV （Kenney）| CC0 |
| `ground_grass.jpg` / `ground_dirt_color.jpg` / `ground_dirt_normal.jpg` | 草地地面贴图 | [ez-tree](https://github.com/dgreenheck/ez-tree) `src/app/public/textures/ground`（经 Git LFS media 取回真实文件）| 见 ez-tree 仓库 LICENSE |
| `eztree_oak.glb` | 复刻 eztree.dev 的真实橡树 | 用 [@dgreenheck/ez-tree](https://github.com/dgreenheck/ez-tree) 库 + `oak_medium` 预设 headless 生成；树皮贴图 Bark001 来自 [ambientCG](https://ambientcg.com/view?id=Bark001)（CC0），叶片贴图 `oak.png` 来自 ez-tree | 库 MIT (© 2024 Daniel Greenheck)；树皮 CC0 |

- 草地场景：`eztree_oak.glb`（复刻 eztree.dev 橡树）作为两侧大树；地面用 `ground_grass.jpg` 平铺 + ez-tree(assets/tree) 的 `grass.glb`/`rock*.glb`/`flower_*.glb` 散布，还原 eztree.dev 草场。`tree.glb` / `pine_tree.glb` 为加载失败时的低模回退。
- 海上城市场景：`business_building.glb` / `house.glb` / `town_center.glb` 天际线建筑；道路用 `road_kit.glb` 的 `road_square` 片平铺，跨于水面之上。
- 星系场景：道路同样用 `road_square` 片但材质改为自发光（霓虹赛道）；地面为 **samplexWave** 波浪方块网格（box 网格 + sin 波浪 + 蓝→粉渐变，程序化生成）；漂浮晶体仍为程序化生成。

加载方式：`index.html` 中 `loadTreeModels()` / `loadBuildingModels()` 用 `GLTFLoader` 载入并经 `gNormalizeProp` 归一化为模板，运行时克隆复用（共享几何/材质）。若加载失败，自动回退到程序化几何，保证可玩性。
