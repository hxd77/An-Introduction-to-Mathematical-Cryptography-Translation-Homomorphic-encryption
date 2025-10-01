# D77CTF

## Chapter2——Web

### 题目2-9：简单的注入

考查点：MySQL报错注入

以sqli-labs第一关为例，进行一个基本的注入。安装sqli-labs省略，直接打开第一关，如下：

![image-20250825011430513](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250825011430513.png)

题目提示输入id参数，因此我们在题目链接后面输入id=1和id=2进行访问，如下图所示：

![image-20250825224010931](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250825224010931.png)

![image-20250825224053018](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250825224053018.png)

我们发现，id=1和id=2的账户和密码信息被显示出来，说明id=1和id=2已被带入到数据库后台中进行查询。继续输入id=1'，即在参数值后面跟上单引号，如下图：

![image-20250825224821445](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250825224821445.png)

可以看到报错信息提示MySQL server version for the right syntax to use near ''1'' LIMIT 0,1' at line 1，这说明我们赋值时添加的单引号已被带入到数据库语句中。它与数据库语句中说明参数范围的前置单引号相闭合，造成原来语句中参数末尾的单引号被剩下，从而导致错误，因此后台语句可能是如下代码：

```mysql
?sql="SELECT * FROM users WHERE id='$id' LIMIT O,1";
```

带入之后变成如下：

```mysql
?sql="SELECT * FROM users WHERE id='1' ' LIMIT O,1";
```

#### 解法一：

**第一步：**

然后采用联合注入，首先知道表格有几列，如果报错就是超过列数，如果显示正常就是没有超出列数。

```mysql
?id=1'order by 3 --+
```

>这段语句的意思是按照第三列默认升序排列，--+后面表示注释。

![image-20250826164035040](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250826164035040.png)

带入之后变成如下：

```mysql
?sql="SELECT * FROM users WHERE id='1' order by 3 --+' LIMIT O,1";
```

![image-20250826164322969](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250826164322969.png)

可以观察到查询是否有4列时报错了，超出了范围，说明只有三列。



**第二步：**

爆出显示位，就是查询表格里面有哪一列是在页面显示的。可以看到是第二列和第三列里面的数据是在页面显示的，而第一列没有在页面显示。

```mysql
?id=-1' union select 1,2,3 --+
```

>这里的select 1,2,3 其实是占位符，因为由前面我们知道这个表一共有三列，所以当我们使用union select来进行联合查询时，必须也要保证返回的列数和之前一样，否则就会报错。如下：
>
>![image-20250826171328711](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250826171328711.png)

![image-20250826170611354](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250826170611354.png)



**第三步：**

获取当前数据名和版本号，这个涉及MySQL数据库的一些函数，通过结果知道当前数据库是security，版本号是5.7.26。

```mysql
?id=-1' union select 1,database(),version()--+
```

![image-20250826191506166](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250826191506166.png)



**第四步：**

爆破表，`information_schema.tables`表示该数据库下的`tables`表。`where`后面是条件，`group_concat()`是将查询到结果连接起来。如果不用`group_concat()`查询到的只有user。该语句的意思是查询information_schema数据库下的tables表里面且table_schema字段内容是security的所有table_name的内容。

```mysql
?id=-1'union select 1,2,group_concat(table_name) from information_schema.tables where table_schema='security'--+
```

>1,2表示占位符，`group_concat` 用于将多个行合并成一个单一的字符串，在这个查询中，它会将数据库中所有表格的名称连接成一个字符串，表名之间由逗号隔开。`information_schema.tables` 是一个系统视图，包含了当前数据库中所有表格的信息。攻击者利用它来查找所有表格的名称。`table_schema='security'` 是条件，限定查询返回的表格仅来自名为 `security` 的数据库。攻击者可以通过修改这个条件来查询不同的数据库中的表格。

![image-20250826193423991](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250826193423991.png)



**第五步：**

爆字段名，我们通过sql语句查询知道当前数据库有四个表，根据表名知道可能用户的账户和密码是在`user`表中。接下来我们就是得到该表下的字段名以及内容。

```mysql
?id=-1'union select 1,2,group_concat(column_name) from information_schema.columns where table_name='users'--+
```

>1,2表示占位符，`group_concat(column_name)`：这是一个 SQL 聚合函数，它将所有的列名（`column_name`）合并成一个单一的字符串。这个函数会将 `users` 表中的所有列名称连接起来，列名之间用逗号分隔。`information_schema.columns` 是一个系统视图，包含了数据库中所有表的列信息。它提供了每个表的列名称、数据类型、长度等信息。攻击者通过它来查询表的列名。`where table_name='users'` 是条件，限制查询仅返回 `users` 表的列信息。

![image-20250826194456992](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250826194456992.png)



**第六步：**

通过上述操作可以得到两个敏感字段就是`username`和`password`，接下来我们就是要得到该字段对应的内容。加了一个`id`可以隔开账户和密码。

```mysql
?id=-1' union select 1,2,group_concat(username ,id , password) from users--+
```

![image-20250827002215340](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250827002215340.png)



#### 解法二：

我们使用sqlmap工具进行注入，简单的sqlmap工具用法如下：（强调的是常用的）

| 参数               | 用途                                                    |
| ------------------ | ------------------------------------------------------- |
| -a、--all          | 获取所有信息                                            |
| -b、--banner       | 获取数据库管理系统的标识                                |
| --current-user     | 获取数据库管理系统的当前用户                            |
| **--current-db**   | **获取数据库管理系统的当前数据库**                      |
| --hostname         | 获取数据库服务器的主机名称                              |
| --is-dba           | 检测DBMS（Database Management System）当前用户是否是DBA |
| --users            | 枚举数据库管理系统用户                                  |
| --passwords        | 枚举数据库管理系统用户密码的哈希                        |
| --privileges       | 枚举数据库管理系统用户的权限                            |
| --roles            | 枚举数据库管理系统用户的角色                            |
| --dbs              | 枚举数据库管理系统数据库                                |
| **--tables**       | **枚举DBMS数据库中的表**                                |
| **--columns**      | **枚举DBMS数据库表列**                                  |
| --schema           | 枚举数据库架构                                          |
| --count            | 检索表的项目数                                          |
| --dump             | 转储数据库表项                                          |
| --dump-all         | 传出数据库所有表项                                      |
| --search           | 搜索列、表和/或数据库名称                               |
| --comments         | 获取DBMS注释                                            |
| **-D DB**          | **指定要进行枚举的数据库名**                            |
| **-T TBL**         | **DBMS数据库表枚举**                                    |
| **-C COL**         | **DBMS数据库表列枚举**                                  |
| -X EXCLUDECOL      | DBMS数据库表不进行枚举                                  |
| -U USER            | 用来进行枚举的数据库用户                                |
| --exclude-sysdbs   | 枚举表时排除系统数据库                                  |
| --pivot-column     | 枢轴列名称                                              |
| --where=DUMPWHERE  | 使用where条件进行表存储                                 |
| --start=LIMITSTART | 获取第一个查询的输出数据位置                            |
| --stop=LIMITSTOP   | 获取最后一个查询的输出数据位置                          |
| --first=FIRSRCHAR  | 第一个查询输出的字符获取                                |
| --last=LASTCHAR    | 最后一个查询输出的字符获取                              |
| --sql-query=QUERY  | 要执行的SQL语句                                         |
| --sql-shell        | 提示交互式SQL的shell                                    |
| --sql-file=SQLFILE | 要执行的SQL文件                                         |

我们在kali中使用参数--current-db判断当前的数据库名称，如下图：

![image-20250830200014638](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250830200014638.png)

![image-20250830200027281](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250830200027281.png)

可以看到当前环境s所连接的数据库名称是secutity，接下来我们要猜测该数据库中的数据表的名称。根据之前的sqlmap参数用法，我们使用--tables参数，注入结果如下：

![image-20250830200448070](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250830200448070.png)

![image-20250830200505330](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250830200505330.png)

可以看看到，在结果中有一个users表。我们对users表进行探测，采用--columns参数判断其中的字段名称，如下图：

![image-20250830201256406](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250830201256406.png)

![image-20250830201412791](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250830201412791.png)

这样我们通过前面几步获取了数据库、表、字段的名称：数据库名是security，表名是users，字段名是id、password和username。

最后一步采用--dump参数将username和password值抓取出来，结果如下：

username值：

![image-20250830201845350](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250830201845350.png)

![image-20250830201908590](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250830201908590.png)

password值：

![image-20250830201928805](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250830201928805.png)

![image-20250830201941965](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250830201941965.png)



### 题目2-10：POST注入

考查点：POST基本注入

以sqli-labs第11关为例：

#### 解法一：

![image-20250921221758735](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250921221758735.png)

从第十一关开始，可以发现页面就发生变化了，是账户登录页面。那么注入点就在输入框里面。前十关使用的是get请求，参数都体现在url上面，而从十一关开始是post请求，参数是在表单里面。我们可以直接在输入框进行注入就行。并且参数不在是一个还是两个。根据前面的认识我们可以猜测sql语句。大概的形式应该是这样username=参数 和 password=参数 ，只是不知道是字符型还是整数型。

当我们输入1时出现错误图片

![image-20250921221921715](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250921221921715.png)

当我们输入1'，出现报错信息。根据报错信息可以推断该sql语句username='参数' 和 password='参数'，说明应该是属于字符型注入。

![image-20250921222528775](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250921222528775.png)

使用`1' or 1=1#`联合注入查询，这里我们使用--+注释就不行，需要换成#来注释：

![’](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250921222955159.png)

和第一关差不多了：

![image-20250921223413959](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250921223413959.png)

#### 解法二：

我们尝试输入`'or 1=1`，得到报错提示，如下图：

![image-20250921223631676](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250921223631676.png)

这说明后台的SQL语句中对于参数的引用使用了单引号（符号注入）。

>可能是`?sql="SELECT * FROM users WHERE id='$id' LIMIT O,1";`
>
>输入后变成了`?sql="SELECT * FROM users WHERE id=''or 1=1' LIMIT O,1";`

输入`admin' or 1=1#`，密码随意或不填，这时将跳转到正确页面，如下：

![image-20250921223928364](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250921223928364.png)

这还没完。继续注入，输入`admin' order by 2#`会返回正确页面，但是`admin ' order by 3#`会报错:

![image-20250921225137089](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250921225137089.png)

### 题目2-11：万能注入

考查点：基本的万能绕过

### 题目2-12：宽字节注入

考查点：MySQL宽字节注入

打开题目后发现是一张美女图片。查看源代码后没有任何提示信息，因此只能分析图片如下：

![image-20250922162025030](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250922162025030.png)

因此我们在Kali的`binwalk`中打开分析：

>`binwalk` 是一个常用的 **二进制文件分析工具**，主要用于 **固件分析与逆向工程**。
>
>它的功能核心在于：
>
>1. **扫描文件中的已知文件类型或数据格式**
>   - `binwalk` 内置了很多 **文件签名（magic signatures）**，比如 JPEG、ZIP、GZIP、PNG、ELF、压缩包等。
>   - 运行时，它会自动在二进制文件里查找这些“特征头”，并列出文件内部包含的各种数据。
>2. **固件提取**
>   - 很多路由器、摄像头、IoT 设备的固件就是一个大文件（可能包含内核、文件系统、压缩包等）。
>   - `binwalk` 可以帮你分离并提取出固件里的 **文件系统（如 squashfs、cramfs、jffs2）**、压缩包等。
>3. **配合解压工具使用**
>   - 结合 `-e` 选项，它会自动调用 `gzip`、`tar`、`unsquashfs` 等解压工具，尝试把提取出的文件直接解压。

![image-20250922162840434](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250922162840434.png)

可以看到此BMP格式图片是有一个压缩文件.zip改成的。改成拓展名为.zip的文件，打开时发现需要密码：

![image-20250922163112704](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250922163112704.png)

我们这里先使用WinRAR修复后再使用ARCHPR的字典模式来进行破解：

>`ARCHPR` 是 **Advanced Archive Password Recovery** 的缩写，中文一般叫 **高级压缩包密码恢复工具**。
>
>它是 **Elcomsoft** 公司出品的一个商用工具，主要功能是用来破解各种压缩包的密码。
>
>------
>
>### 主要功能
>
>1. **支持的格式**
>   - ZIP（WinZip、PKZip、InfoZip 等）
>   - RAR（1.x ~ 5.x）
>   - ARJ、ACE、CAB 等常见压缩格式
>2. **破解方法**
>   - **字典攻击**：利用常见密码字典尝试。
>   - **暴力破解**：逐个字符组合尝试。
>   - **掩码攻击**：用户已知部分密码特征（如长度、开头字母），缩小范围。
>   - **已知明文攻击**：如果有压缩包中部分文件的明文，可以加速破解。
>3. **优化**
>   - 对某些加密方式有优化算法，比单纯暴力快。
>   - 可以利用多核 CPU 提高速度。

![image-20250922163940508](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250922163940508.png)

我们知道压缩包的密码是6666.如下图所示，打开TXT文件，其提示内容要求我们输入账户和密码：

![image-20250922164049562](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250922164049562.png)



代码审计是企业安全体系建设中非常重要的一环，通常是企业的重点工作。再CTF的Web类题目中，PHP代码审计是最常考的内容之一。这一方面是因为Internet上的很多网站采用PHP语言进行开发；另一方面是因为PHP语言中的很多函数和变量有缺陷，所以导致大量的Web安全问题与PHP相关。

### 题目2-13：小试身手

考查点：md5()函数的漏洞

打开题目链接，可查看到源代码信息，如下图：

![image-20250922165750952](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250922165750952.png)

显然，这属于代码审计的范畴，而看代码的关键是看相关的`条件判断句`。因此重点在于通过GET方法传入的参数不能和字符'240610708'相等，并且传入的变量被PHP中的md5()函数计算后的哈希值要与240610708进行md5运算后的哈希值相等。在密码学中，md5()函数属于抗碰撞哈希函数，也就是无法找到另一个消息`md5(GET['md5'])=md5('240610708')。`我们该如何进行下去呢？去官网查看md5()函数，如下图：

![image-20250922170409198](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250922170409198.png)

可以看到，md5对于输入的string做了处理，输出了一段字符串，然后程序比较这两段哈希值是否相等（用==表示）。再次查看PHP对于哈希值的比较，就会发现问题。

PHP在处理哈希字符串时会利用!=或==对哈希值进行比较，它把每一个`0E`开头的哈希值都解释为0。如果两个不同的变量经过哈希后，其哈希值都是以`0E`开头，那么PHP将认为它们时相同的(都是0)。因此我们需要找到一个字符串，让它满足不等于'240610708'和md5()计算后以0E开头这两个条件。通过搜索引擎搜到的以0E开头的答案有很多，可使用其中一个，输入后得到flag值，如下：

>因为这是PHP中的弱比较==问题：
>
>- 假设两个不同的字符串，经过 MD5/SHA1 等哈希后，得到的哈希都是类似：
>
>```
>0e123456789... 
>0e987654321...
>```
>
>- 都以 `"0e"` 开头，后面全是数字。
>- PHP 的 `==` 比较：
>
>```
>md5("str1") == md5("str2")
>```
>
>- 如果返回的 MD5 值都是 `"0e12345..."` 和 `"0e98765..."`，PHP 会**把它们当作科学计数法的数字**：
>  - `"0e12345"` → 0 × 10^12345 → 数字 0
>  - `"0e98765"` → 0 × 10^98765 → 数字 0
>- 因此：
>
>```
>"0e12345" == "0e98765"  // true
>```

![image-20250922171232262](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250922171232262.png)



### 题目2-14: 小小加密

考查点：strrev、strlen、substr、str_rot13和base64_encode函数的特性

打开题目链接，得到的提示为"flag的密文：=pJovuTsWOUrtIJZtcKZ2OJMzEJZyMTLdIas,请解密！"，如下图所示：

![image-20250927152729251](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250927152729251.png)

观察该代码，改代码首先对我们输入的变量str进行反转得到\$_o，接着通过一个for循环对反转后的字符串坐处理：第一步取\$o的每一位的值；第二步对得到的值进行ASCII码值并加1得到一个数字；第三步对得到的数字取字符；最后将所有字符进行拼接得到值\$\_。之后对\$\_进行Base64编码，然后反转，最后进行Rot13编码得到的输出值就是我们在上面看到的flag的密文值，因此我们进行解密编程的思路如下：

1. `str_rot13` → 还原 ROT13
2. `strrev` → 还原反转
3. `base64_decode` → 还原原始字节序列
4. 每个字符 **ASCII -1**
5. `strrev` → 还原输入

>ROT13 = 把字母表 **循环右移 13 位**。
>
>英文字母表总共有 **26 个字母**。
>
>所以再移 13 位，正好回到原位：

代码如下：

```php
<?php
function decode($str){
    //1.ROT13还原
    $_=str_rot13($str);
    //2. 反转回来
    $_=strrev($_);
    //3.base64解码
    $_=base64_decode($_);
    //4.每个字符-1
    $out="";
    for($i=0;$i<strlen($_);$i++)
    {
        $c=substr($_,$i,1);
        $out.=chr(ord($c)-1);
    }

    //5.最终再反转
    return strrev($out);
}
echo decode("=pJovuTsWOUrtIJZtcKZ2OJMzEJZyMTLdIas");
?>
```

运行后得到flag：

![image-20250927155716333](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250927155716333.png)



### 题目：2-15：你不知道的事

考查点：sha1函数的特性

打开题目如下：

![image-20250927155918527](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250927155918527.png)

首先查看源代码：

![image-20250927155949357](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250927155949357.png)

看到注释看到有提示查看备份文件index.phps，查看其代码，如下：

![image-20250927161759063](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250927161759063.png)

通过分析代码，可以看出程序通过GET方法传入两个参数`name`和`passwd`。其第一个条件是`name`和`passwd`不能相等。第二个条件是`name`和`passwd`的值在经过sha1函数处理后得到的散列值在PHP模式下进行比较要想等。在这里，我们需要了解的是sha1函数对处理对象的选择和对返回类型的处理。如下图所示，通过PHP手册查看sha1函数的使用方法和特性，如下图：

![image-20250927221523796](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250927221523796.png)

可以看到sha1()函数在此处理的字符串值。我们通过脚本测试sha1()函数对于其他值的处理，如下图：

```php
<?php
$str='123456';              // 定义一个字符串变量 $str
$inter=1234;                // 定义一个整型变量 $inter
$arr=array('xw');           // 定义一个数组 $arr，里面只有一个元素 "xw"

print sha1($str);           // 对字符串 "123456" 计算 sha1 值
print sha1($inter);         // 对整数 1234 计算 sha1 值（会被转成字符串 "1234"）
print sha1($arr);           // 对数组调用 sha1()，这是不允许的，会报错
?>
```

可以看到sha1()函数在处理数组时报错，提示因sha1()函数只接受字符串参数。在此题中，要求name和password两个参数值本身不相等却要求sha1()函数处理后的值相等，这在密码学上不符合哈希函数的强抗碰撞性，即要找到散列值相同的两条不同消息是非常困难的。我们可以构造两个两个参数都是数组类型的变量值代入，以改变参数类型，使得sha1()函数在处理数组对象时报错。由于对于两个不同的数组处理后的结果肯定是一样的，因而可以达到绕过的目的。完整的绕过参数如下：

```php
name[]=1&password[]=2
```

如下图所示：

![image-20251001001102655](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20251001001102655.png)



### 题目2-16：科学计数法

考查点：PHP中科学记数法的表示

打开题目如下：

![image-20251001001310363](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20251001001310363.png)

题目给的代码信息如下：

```php
<?php

$flag = '*********';

if (isset($_GET['password'])) {

	if (is_numeric($_GET['password'])){

		if (strlen($_GET['password']) < 4){

			if ($_GET['password'] > 999)

				die($flag);

			else

				print '<p class="alert">Too little</p>';

		} else

				print '<p class="alert">Too long</p>';

	} else

		print '<p class="alert">Password is not numeric</p>';

}

?>
```

它通过三个条件判断让我们对参数password进行赋值，要求password是整数，其长度小于4且值大于999。当这三个条件同时满足时，才会将flag值显示出来。显然要用科学计数法。如果我们在PHP代码中定义的一个数字很长（这在有些语义环境中可能并不合适），那么可以通过科学记数法将其打印出来，如下图所示：

```php
<?php
$number=120000000000000000000;
$result=sprintf("%e", $number);//// 用科学计数法格式化，比如 "1.200000e+20"
$afterformat=str_replace("e+","* 10^",$result);
//在字符串 $result 里，把所有的 "e+" 替换成 "* 10^"，并把结果赋值给 $afterformat。
echo $afterformat;
?>
```

输出结果为`1.200000* 10^20`。这里我们将一个22位的数字通过指数幂表示出来，而`1.200000* 10^20`也可以表示为`1.2e20（不能写为1.2e+20）`，因此在此题中，我们通过对1eN进行flag值的获取。再次查看之前的条件，大于999的最小整数是1000，如下图表示为1e3带入：

![image-20251001003404727](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20251001003404727.png)



### 题目2-17：反序列化与文件包含

考查点：有关PHP序列化和反序列化的基本知识

反序列化是近几年频繁出现的漏洞之一，下面我们介绍序列化和反序列化的概念。
