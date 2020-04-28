# xjbx-QQ-group-bot
一个基于NoneBot的xjbx的Q群机器人，完全属于xjb写的范畴。功能很杂乱，包括[nbnhhsh](https://github.com/itorr/nbnhhsh?files=1)、图片搜索、rss订阅等各种乱七八糟的功能。基本上就是我网上看到的和一拍脑袋想出来的功能大杂烩。

# 安装

目前没有考虑安装问题。如果你看得懂源码的话，可以尝试部署一下。后续可能会加入部署功能。

# Simple Usage

目前该机器人支持以下功能：

+ st

    说明：向机器人发送`st`，然后发送你想搜索的图片。机器人会帮你搜索图片来源。

+ bilibili

    说明：向机器人发送`bilibili`（或者短命令`bili`），再发送你想搜索的内容，机器人会返回根据关键字在b站搜索的结果。群聊默认返回 **1** 个结果，私聊默认返回 **5** 个结果。

+ hhsh

    说明：向机器人发送`hhsh`+你想搜索的汉字首字母简写，以空格分开。机器人会调用 [nbnhhsh](https://github.com/itorr/nbnhhsh) 的api搜索该简写代表的真实含义。如果你对搜索结果不满意，可以去 [这里](https://lab.magiconch.com/nbnhhsh/) 提交新简写及其含义。

+ rss

    说明：该功能用于订阅消息源的消息，该功能基于 [Rsshub](https://github.com/DIYgod/RSSHub)。由于我很懒，所以现在只支持三个订阅源。向机器人发送`rss`，然后按机器人的引导来就行了。同时，加上`-s`参数可以订阅消息源，不加的话就是仅查看最新消息。

# Advanced Usage    

由于我很懒，所以高级用法自己看看源码吧（QwQ），但是基本用法已经够用了。

# 鸣谢

+ [[开源] 二次元搜图QQ机器人](https://github.com/Tsuk1ko/CQ-picfinder-robot) 一开始就想把这个插件的功能加到我的机器人里面，无奈博主是用我不会的语言写的，既然抄不了就只能自己手撸一个了。当然他的源码也很有启发性，API也很好用！
+ [nbnhhsh](https://github.com/itorr/nbnhhsh) 只能说这玩意太有意思了！（就是访问速度有点不太理想
+ [Rsshub](https://github.com/DIYgod/RSSHub) 整个`rss`都依赖于它了，我怎么能不感谢呢？
+ [SauceNAO](https://saucenao.com) `st`功能有很大一部分都是依赖于它的，同样表示感谢！
+ [哔哩哔哩](https://www.bilibili.com)
