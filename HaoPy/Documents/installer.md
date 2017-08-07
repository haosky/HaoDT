## 部署storm+kafka查重程序

### 1.修改配置项：Integration\HaoPy\gxstorm\check_repeat\sim_settings.properties


```[hbase_table]

caizheng_table=CaiZhengMoNiSim

hbase上存储专项资金的表，有以下字段

["project", "finical_unit", "finical_name", "date", "doc", "content", "unit", "finical","fl_type"]

---
exists_table=CaiZhengMoNi_SamExists

查重记录存在表，可以通过这张表判断数据库是否有查重记录

---

phase_table=CaiZhengMoNi_SamPhase

查重记录表，已经查重的表会存储相关记录信息在这张表上，下次用户操作的时候，直接查询结果
---
```

###2.修改配置项：Integration\HaoPy\gxkafka\kafka.properties
```
[server]

broker_hosts=192.168.1.122

kafka的主机ip地址

---

zookeeper_hosts=192.168.1.122:2181

kafka的zookeeper ip地址
---
```


###3.发布storm程序
```
运行pyton程序 Integration\HaoPy\develop\deploy_intranet.py

详细情况查看代码

修改代码的 env.host_string = "192.168.1.122" ip地址代表要部署的机器

如果发布正常则会生成storm Topology
查看页面 http://192.168.1.122:8080 的storm页面，具体端口由storm配置决定

```

###4.运行服务端
```
Integration\HaoPy\gxthrift\simhandler\servers\sim_develop_v2.py

修改python代码developer类的属性变量

SERVER_HOST = '192.168.18.152'

SERVER_PORT = 9994

```

###5.客户端配置项
```
Integration\DataServerV1\sources\tserverSettings.properties

gxthrift.sim_develop.host=192.168.18.152

对应服务端机器的ip
---
gxthrift.sim_develop.port=9994

对应服务端机器的端口
---

```