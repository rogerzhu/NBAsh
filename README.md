# 用命令行看NBA直播

## 运行该程序的依赖项
如果想运行起这个程序，需要首先安装如下的库先：
```
pip3 install asciimatics
pip3 install requests
pip3 install BeautifulSoup4
pip3 install fake-useragent
```

运行方法，进入NBash.py所在目录，输入：
```
python3 ./NBash.py
```

## 这是什么
这是一个使用命令行就能实时显示当天NBA比赛的程序，包括对阵双方，比分以及进行时间，并且可以查看每场比赛的球员数据（～～特别适用于上班摸鱼～～）。目前所有直播信息以及数据都来自于[虎扑](https://nba.hupu.com/games)，没错，我就是一名虎扑jr，后面我修改程序（虽然心中想每个数据源封装一个类，然后采用工厂模式，但手暂时还没有这么做），争取使用多种源，展示效果如下：
![nbalivecmd.gif](https://i.loli.net/2019/11/21/JjaGl5nK16dChzS.gif)

如果命令行宽度小于190个字符，那么，程序会显示一个缩减版的数据展示：
![缩减版.png](https://i.loli.net/2019/11/21/VOZv4u8fnPWxtTc.png)

为了最大限度的不骚扰数据源的服务器，特地加入逻辑，如果所有场次都结束了，那么就不再每隔几秒去扒数据了，就扒一次就可以了。

## 未来的想法
- [ ] 继续优化代码结构，可以更方便的切换不同的数据源
- [ ] 目前虽然定义了诸如Game,Team,Player的类，但是还没有做具体的记录工作
- [ ] 在优化速度的路上永不停歇
- [ ] 分别在Windows和Mac平台上打包成可执行程序，方便一般用户使用
- [ ] 修改任何bug以及反直觉使用的地方




