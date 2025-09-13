# 《An Introduction to Mathematical Cryptography》第七章翻译



## 前言

因为我是做有关FHE方面的，所以我需要了解一些有关格的知识才能了解FHE的一些算法。本教材是一本非常优秀的英文教材。这也是我上网偶然间发现的。现在让我们来开始学习。



我们之前研究过的所有公钥密码系统，其安全性要么直接、间接地基于两大难题：一是大数分解难题，二是有限群中的离散对数求解难题。在本章中，我们将探讨一种源于格理论的新型难题，这种难题可作为公钥密码系统的基础。与早期的密码系统相比，基于格的密码系统具有若干潜在优势，包括更快的加密 / 解密速度以及所谓的抗量子性。后者意味着目前还没有已知的量子算法能够快速解决困难的格问题（参见 8.11 节）。此外，我们将会发现，格理论在密码学中的应用不仅仅是提供一种新的困难问题来源。

回想一下，实数域上的$\R$向量空间 $V$是一组向量的集合，在这个集合中，两个向量可以相加，一个向量可以与一个实数相乘。格与向量空间类似，不同之处在于，在格中我们只能将向量与整数相乘。这个看似微小的限制却引发了许多有趣且微妙的问题。由于格这一主题可能显得有些深奥，与密码学的日常实际应用相去甚远，因此在本章开头，我们将给出两个启发性的例子。在这些例子中，我们不会提及格，但格其实就隐藏在背景中，有待在密码分析中发挥作用。之后，我们会在 7.3 节回顾向量空间理论，并在 7.4 节正式引入格的概念。



## 7.1 一种同余公钥密码系统

这一节我们介绍一个真实的公钥密码系统的简单模型(toy model)。这个版本与二维格有关，因此存在致命的弱点，因为其维度太低。然而，它作为一个示例，说明了即使底层的困难问题看似与格无关，格在密码分析中也可能出现。此外，它提供了对 NTRU 公钥密码系统的最低维度介绍，该系统将在后面描述。

Alice 首先选择一个大的正整数 $q$ 作为公共参数，然后选择另外两个秘密的正整数 $f$ 和 $g$，满足：

$f<\sqrt{q/2},\quad \sqrt{q/4}<g<\sqrt{q/2},\quad\text{and}\quad\gcd(f,q)=1.\\$

Alice 随后计算：

$h\equiv f^{-1}g\pmod{q}\quad\text{with}\quad0<h<q.\\$

**这里 $f^{-1}$ 是 $f$ 关于模 $q$ 的逆元**。注意到与 $q$ 相比 $f,g$ 都比较小，都是 $O(\sqrt{q})$ 的数量级，而 $h$ 是 $O(q)$的数量级，相对更大一些。**Alice 的私钥是小整数 $f,g$，公钥是大整数 $h$**。

为了发送消息，Bob 选择明文 $m$ 和随机数 $r$ （临时密钥，ephemeral key）满足不等式：

$0<m<\sqrt{q/4}\quad\text{and}\quad 0<r<\sqrt{q/2}.\\$

他计算密文：

$e\equiv rh+m\pmod{q}\quad\text{with}\ 0<e<q\\$

并发送给 Alice.

Alice 进行解密，首先计算：

$a\equiv fe\pmod{q}\quad\text{with}\ 0<a<q,\\$

再计算

$b\equiv f^{-1}a\pmod{g}\quad\text{with}\ 0<b<g.\\$

**注意这一步的 $f^{-1}$ 是 $f$ 关于模 $g$ 的逆元。**

我们现在验证 $b=m$，即通过这种方式 Alice 能够成功恢复出 Bob 的明文。观察到 $a$ 满足：

$a\equiv fe\equiv f(rh+m)\equiv frf^{-1}g+fm\equiv rg+fm\pmod{q}.\\$

对 $f,g,r,m$ 大小的限制表明了 $rg+fm$ 是小的整数：

$rg+fm<\sqrt{\frac{q}{2}}\sqrt{\frac{q}{2}}+\sqrt{\frac{q}{2}}\sqrt{\frac{q}{4}}<q.\\$

因此 $0<a<q$，同余式 $a\equiv fe\pmod{q}$ 便转化为了等式

$a=fe=rg+fm.$

最后 Alice 计算：

$b\equiv f^{-1}a\equiv f^{-1}(rg+fm)\equiv f^{-1}fm\equiv m \pmod{g}\quad\text{with}\ 0<b<g.\\$

因为 $m<\sqrt{q/4}<g$，则 $b=m$。下图总结了同余密码系统（congruential cryptosystem）。

![](https://pic4.zhimg.com/v2-871196e3b7dfd62d2b3291e21f6704f1_1440w.jpg)

图 1. 同余公钥密码系统，源自《An Introduction to Mathematical Cryptography》



_Example._ Alice 选择

$q =122430513841,\quad f= 231231,\quad \text{and}\quad g = 195698.\\$

这里 $f\approx 0.66\sqrt{q},g\approx 0.56\sqrt{q}$ 都是被允许的值。Alice 计算：

$f^{−1} \equiv 49194372303 \pmod{q} \quad\text{and} \quad h\equiv f^{−1}g \equiv 39245579300 \pmod{q}.\\$

Alice 的公钥为 $(q,h)=(122430513841,39245579300)$。

Bob 决定发送给 Alice 明文 $m=123456$，随机数为 $r=101010$。他使用 Alice 的公钥来计算密文：

$e\equiv rh+m\equiv 18357558717\pmod{q},\\$

并将密文发送给 Alice。

为了解密 $e$，Alice 首先用 $f$ 计算：

$a\equiv fe\equiv48314309316 \pmod{q}.\\$

注意到 $a=48314309316 < 122430513841 = q$。她再利用 $f^{-1}\equiv 193495 \pmod{g} $ 来计算：

$f^{−1}a \equiv 193495\cdot48314309316 \equiv 123456 \pmod{g},\\$

与理论相符，结果就是 Bob 的明文。

Eve 如何攻击这个系统呢？她可能尝试暴力搜索所有可能的私钥值或者所有可能的明文值，但是这都需要 $O(q)$ 数量级的操作。让我们更详细地考虑一下 Eve 的任务如果她尝试从已知的公钥 $(q,h)$ 中得到私钥 $(f,g)$。不难看出如果 Eve 能够找到任意的正整数对 $F,G$ 满足：

$Fh\equiv G\pmod{q}\quad\text{and}\quad F=O(\sqrt{q})\quad\text{and}\quad G=O(\sqrt{q}),\\$

那么 $(F,G)$ 就很有可能是解密密钥。重写上面的同余式为等式 $Fh=G+qR$，我们将 Eve 的任务重新表述为寻找一对相对较小的整数 $(F, G)$，满足以下性质：

$F\underbrace{(1,h)}_{\text{known}}-R\underbrace{(0,q)}_{\text{known}}=\overbrace{(F,G)}^{\text{unknown}}.\\$

相当于是

$$ (F,Fh)-(0,Rq)=(F,G)$$

$F,R$ 是未知的整数，$(1,h),(0,q)$ 是已知的向量，$(F,G)$ 是未知的小向量。

因此 Eve 知道两个向量 $v_1=(1,h),v_2=(0,q)$，每一个的长度都是 $O(q)$（因为 $0<h<q$ ），她想要找到一个线性组合 $w=a_1 v_1+a_2v_2$ 满足 $w$ 的长度为 $O(\sqrt{q})$（这是因为$F=O(\sqrt{q})\quad\text{and}\quad G=O(\sqrt{q})$），但是注意 $a_1,a_2$ 都需要是整数，因此 Eve 需要在下面的向量集合中找到一个短的非零向量：

$L=\{a_1v_1+a_2v_2: a_1,a_2\in\mathbb{Z}\}.\\$

这个集合 $L$ 就是 2 维格的一个例子。它看起来非常像由基底 $\{v_1,v_2\}$ 生成的 2 维向量空间，除了线性组合的系数只能取整数。

在上面的例子中，寻找 2 维格中的短向量存在非常快速的方法求解。这个方法是由 Gauss 提出的，在格约化一节中有描述。





## 7.2 子集和问题与背包密码系统

第一个基于 $\mathcal{NP}$ 完全问题的密码系统是由 Merkle 和 Hellman 在20世纪70年代末设计的。他们使用了以下数学问题的一个变体，该问题是经典背包问题的推广。

![](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/v2-83c85b61b4f64556a015a83c9c4f4465_1440w.jpg)

图 2. 子集求和问题，源自《An Introduction to Mathematical Cryptography》

_Example._ 令 $M=(2,3,4,9,14,23),S=27$。那么经过几次尝试就能得到子集合 $\{4,9,14\}$ 的和是 $27$，不能验证这是唯一的子集合满足和为 $27$。类似地，如果我们取 $S=29$，那么我们能够找到 $\{2,4,23\}$ 满足条件，但是这种情况还有第二个解 $\{2,4,9,14\}$。

还有另一种描述子集求和问题的方式。序列：

$M=(M_1,M_2,\dots,M_n)\\$

是公开的正整数。Bob 选择一个秘密的二进制向量(binary vector) $x=(x_1,x_2,\dots,x_n)$，**即每一个 $x_i$ 要么取 0 要么取 1**。Bob 计算和：

$S=\sum_{i=1}^n x_i M_i\\$

并将 $S$ 发给 Alice。子集和问题要求 Alice 要么找到原始的向量 $x$，要么找到另一个二进制向量，能够给出相同的和。注意向量 $x$ 告诉 Alice 哪一个 $M_i$ 被包含进 $S$，因为 $M_i$ 在和式 $S$ 中当且仅当 $x_i=1$。因此只要确定了二元向量 $x$ 就是确定了 $M$ 的一个子集合。

显然，Alice 能够遍历所有 $2^n$ 个 $n$ 长的二元向量来找到 $x$。一个简单的碰撞算法可以将复杂度的指数减半。



**Proposition.** 令 $M=(M_1,M_2,\dots,M_n)$ 并令 $(M,S)$ 表示一个子集和问题。对于所有满足下面条件的整数集合 $I$ 和 $J$：

$I\subset \{i:1 \leq i\leq \frac{1}{2}n\}\quad\text{with}\quad J\subset \{j:\frac{1}{2}n < j \leq n\}\\$

计算得到两个序列：

$A_I=\sum_{i \in I}M_i\quad\text{and}\quad B_J=S-\sum_{j\in J}M_j.\\$

那么这些序列包含一对集合 $I_0,J_0$ 满足 $A_{I_0}=B_{J_0}$，并且集合 $I_0,J_0$ 给出了一个子集和问题的解：

$S=\sum_{i \in I_0}M_i+\sum_{j \in J_0}M_j.\\$

每个序列的条目最多有 $2^{n/2}$ 项，所以算法的运行时间为 $O(2^{n/2+\epsilon})$，其中 $\epsilon$ 是序列的排序和比较所引入的小值。


**_Proof._** 如果 $x$ 是一个二进制向量，它是给定的子集和问题的一个解，那么我们可以将该解写作:

$\sum_{1\leq i\leq \frac{1}{2}n}x_iM_i=S-\sum_{\frac{1}{2}n< i\leq n}x_iM_i.\\$

子集合 $I,J$ 的个数均为 $O(2^{n/2})$。

如果 $n$ 很大，那么一般来说解决一个随机的子集和问题的实例是很困难的。然而，我们假设 Alice 拥有关于 $M$ 的某些秘密知识或陷门（trapdoor）信息，使得她能够确保解 $x$ 是唯一的，并且允许她很容易地找到 $x$。那么 Alice 可以将子集和问题用作公钥加密系统。Bob 的明文是向量 $x$，他的加密消息是和 $S = \sum x_iM_i$，只有Alice可以轻松从已知的 $S$ 中恢复 $x$。

但是，Alice 可以使用什么技巧来确保她可以解决这个特定的子集和问题而其他人却不能呢？一种可能性是使用一个极其容易解决的子集和问题，但以某种方式对其他人隐藏了这个简单的解决方案。



**Definition.** 一个整数的超递增序列（superincreasing sequence）是正整数序列 $r=(r_1,r_2,\dots,r_n)$ 满足性质：

$r_{i+1}\geq 2r_i\quad\text{for all }1\leq i\leq n-1.\\$

下面的估计解释了这个序列的名字。



**Lemma.** 设 $r=(r_1,\dots,r_n)$ 是一个超递增序列。那么

$r_k > r_{k-1}+\dots+r_2+r_1 \quad\text{for all }2\leq k\leq n. \\$



**_Proof._** 我们通过对 $k$ 进行归纳来给出证明。对于 $k=2$ 我们有 $r_2\geq 2r_1 >r_1$，是归纳基础。现在我们假设上面的引理对于 $2\leq k< n$ 是正确的，那么用超递增序列的性质和归纳假设，我们能够得到：

$r_{k+1}\geq 2r_k=r_k+r_k>r_k+2r_{k-1} >r_k +(r_{k−1} +···+r_2 +r_1).\\$

这就证明了引理对于 $k+1$ 也是正确的。

**当 $M$ 中的整数形成一个超递增序列时，子集和问题是非常容易解决的。**



**Proposition.** 设 $(M,S)$ 是一个子集和问题，其中 $M$ 中的整数形成一个超递增序列。假设存在一个解 $x$，那么它是唯一的且能够用下面的算法快速计算得到：

![](https://pica.zhimg.com/v2-8aaa93050545ca31fd595ecc81e15e8c_1440w.jpg)

图 3. 快速计算SSP的一个解，源自《An Introduction to Mathematical Cryptography》



**_Proof._** $M$ 是一个超递增序列意味着 $M_{i+1}\geq 2M_i$ 。我们知道存在一个解，因此为了将它与算法产生的向量 $x$ 区分开，我们将实际的解称为 $y$ 。因此我们假设 $yM=S$ ，我们需要证明 $x=y$ 。

我们用逆向归纳法（downward induction）证明 $x_k=y_k$ 对于所有的 $1\leq k\leq n$ 都成立。**我们的归纳假设是对于 $k<i\leq n$，$x_i=y_i$**，我们需要证明 $x_k=y_k$。注意我们允许 $k = n$，在这种情况下，我们的归纳假设是自动成立的。根据归纳假设，当我们从 $i=n$ 开始执行算法到 $i=k+1$ 时（逆向执行），在每一阶段我们都有 $x_i=y_i$。因此在执行第 $i=k$ 次循环时，$S$ 的值已经被化简为：

$S_k=S-\sum_{i=k+1}^n x_iM_i=\sum_{i=1}^ny_iM_i-\sum_{i=k+1}^n x_iM_i=\sum_{i=1}^k y_iM_i.\\$

当执行第 $i=k$ 次循环时，可能有两种情况发生：

$\begin{align}(1)\quad &y_k=1 \ \Longrightarrow\ S_k\geq M_k &\Longrightarrow\ &x_k=1,\quad \sqrt{}\\(2)\quad &y_k=0 \ \Longrightarrow\ S_k\leq M_{k-1}+\dots+M_1<M_k &\Longrightarrow\ &x_k=0,\quad \sqrt{}\end{align}$

情况(2)我们使用了上面的引理推导出 $M_{k-1}+\dots+M_1$ 严格小于 $M_k$，这两种情况我们都能得到 $x_k=y_k$，这就完成了 $x=y$ 的证明。此外，这也表明解是唯一的，因为我们已经证明了任何解都与算法的输出一致，而算法本质上对于任何给定的输入 $S$ 都返回一个唯一的向量 $x$。

**_Example._** 集合 $M=(3,11,24,50,115)$ 是超递增的。我们令 $S=142$ 是 $M$ 中一些元素的和。首先 $S\geq 115$，所以 $x_5=1$，我们将 $S$ 替换为 $S-115=27$。接下来 $27<50$，所以 $x_4=0$。继续，$27\geq 24$，所以 $x_3=1$，此时 $S$ 变为了 $27-24=3$。$3<11$，所以 $x_2=0$。最后 $3\geq 3$，所以 $x_1=1$。注意 $S$ 已经被减为 $3-3=0$ 了，于是 $x=(1,0,1,0,1)$ 就是一个解。检查我们的答案：

$1\cdot3+0\cdot11+1\cdot24+0\cdot50+1\cdot115 = 142.\quad \sqrt{}\\$

Merkle 和 Hellman 提出了一个基于超递增子集和问题的公钥密码系统，该系统使用同余来伪装（disguise）。为了创建公/私钥对，Alice 选择一个超递增序列 $r = (r_1,\dots,r_n)$。再选择两个大的秘密整数 $A$ 和 $B$ 满足：

$B>2r_n\quad\text{and}\quad\gcd(A,B)=1.\\$

Alice 再构造一个新的**非超递增序列 $M$**，其中：

$M_i \equiv Ar_i \pmod{B}\quad\text{with }0\leq M_i <B.\\$

**序列 $M$ 就是 Alice 的公钥。**

为了加密消息，**Bob 选择二进制向量 $x$ 作为明文**，计算密文发送给 Alice:

$S=x\cdot  M=\sum_{i=1}^nx_iM_i.\\$

为了解密，Alice 首先计算：

$S'\equiv A^{-1}S\pmod{B}\quad\text{with }0\leq S'<B.\\$

然后，Alice 用超递增序列 $r$ 和上面命题提到的快速算法来解决 $S'$ 的子集和问题。

这样做能够成功解密是因为：

$S'\equiv A^{-1}S\equiv A^{-1}\sum_{i=1}^nx_iM_i\equiv A^{-1}\sum_{i=1}^nx_iAr_i\equiv\sum_{i=1}^n x_ir_i\pmod{B}.\\$

根据假设 $B>2r_n$ 和引理：

$\sum_{i=1}^nx_ir_i \leq \sum_{i=1}^nr_i<2r_n<B,\\$

所以同余式就变成了等式 $S'=\sum x_ir_i$，$S'$ 的取值范围是 $0$ 到 $B-1$。

下图总结了 Merkle-Hellman 密码系统：

![](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/v2-13f275396c745110b30a1119434440b1_1440w.jpg)

图 4. Merkle-Hellman 子集求和密码系统，源自《An Introduction to Mathematical Cryptography》



**_Example._** 设 $r =(3,11,24,50,115)$ 是 Alice 的秘密超递增序列，$A=113,B=250$ 是她所选的秘密大整数。那么她的伪装序列为：

$\begin{align}M &\equiv (113\cdot3,113\cdot11,113\cdot24,113\cdot50,113\cdot115) \pmod{250}\\&=(89,243,212,150,245). \end{align}\\$

注意到 $M$ 序列远不是超递增的（即使她重新排列项，使其递增）。  
Bob 决定向 Alice 发送秘密信息 $x = (1,0,1,0,1)$。他加密 $x$ 通过计算：

$S=x\cdot M=1\cdot89+0\cdot243+1\cdot212+0\cdot150+1\cdot245=546.\\$

在收到 $S$ 后，Alice 将其乘以 177，即 113 模 250 的逆，得到：

$S'\equiv 177\cdot 546 = 142 \pmod{250}.\\$

随后，Alice 用命题的快速算法来求解 $S'=x\cdot r$，恢复出明文 $x$。

基于伪装子集和问题的加密系统被称为**子集和密码系统（subset-sum cryptosystems）或背包密码系统（knapsack cryptosystems）**。其基本思想是从一个秘密的超递增序列开始，使用秘密的模线性运算对其进行伪装，并将伪装后的序列作为公钥发布。Merkle 和 Hellman 最初的系统建议对 $Ar\pmod{B}$ 的条目应用秘密置换作为额外的安全层。后来的版本由许多人提出，涉及对一些不同的模数进行多次乘法和约减。关于背包加密系统的优秀综述，可以参阅 Odlyzko 的文章（The Rise and Fall of Knapsack Cryptosystems）。



**_Remark._** 关于背包系统必须考虑的一个重要问题是达到期望的安全级别所需的各种参数的大小。有 **$2^n$ 个二进制向量 $x=(x_1,\dots,x_n)$**，我们已经在本节的第一个命题中看到，存在一个碰撞算法，因此可以在 $O(2^{n/2})$ 次运算中破解背包加密系统。因此，为了获得 $2^k$ 数量级的安全性，有必要取 $n>2k$，例如，$2^{80}$ 安全性需要 $n>160$。尽管这提供了针对碰撞攻击的安全性，但并不排除存在其他更有效攻击的可能性，我们将在最后一节看到，这些攻击实际上是存在的。



**_Remark._** 假设我们已经选择了 $n$，那么其他参数应该选择多大的呢？事实证明，如果 $r_1$ 太小，就会有简单的攻击方法，所以必须要令 $r_1>2^n$。序列的超递增性质意味着：

$r_n > 2r_{n−1} > 4r_{n−2} > \dots> 2^nr_1 > 2^{2n}.\\$

那么 $B>2r_n=2^{2n+1}$，所以我们得到了公钥 $M_i$ 和密文 $S$ 满足：

$M_i=O(2^{2n})\quad\text{and}\quad S=O(2^{2n}).\\$

因此，公钥 $M$ 是一个包含 $n$ 个整数的序列，每个整数大约有 $2n$ 位长，而明文 $x$ 包含 $n$ 位信息，密文大约有 $2n$ 位。注意到消息的扩展比为 $2:1$。  
例如，假设 $n=160$。那么公钥大小大约为 $2n\cdot n=51200$ 位。与 RSA 或 Diffie-Hellman 相比，对于 $2^{80}$ 数量级的安全性，它们的公钥大小大约只有 1000 位。这个较大的密钥尺寸可能看起来是一个很大的缺点，但它会被背包系统极快的处理速度所弥补。事实上，背包系统的解密只需要一次(或很少几次)的模乘运算，而加密根本不需要。这比 RSA 和 Diffie-Hellman 使用大量计算密集型的模幂运算要高效得多。从历史上看，这使得背包密码系统具有非常大的吸引力。



**_Remark._** 已知的解决随机选择的子集和问题的最佳算法是碰撞算法，如前面命题已经提到的。不幸的是，随机选择的子集和问题没有陷门，因此不能用于创建密码系统。事实证明，使用伪装的超递增子集和问题有其他更有效的攻击算法。第一种此类攻击由 Shamir、Odlyzko、Lagarias 等人使用各种特设的方法（ad hoc methods），但在 1985 年著名的 LLL 格约化论文发表之后，很明显，基于背包的加密系统存在根本缺陷。粗略地说，如果 $n$ 小于 300 左右，那么格约化允许攻击者在短时间内从密文 $S$ 中恢复明文 $x$。因此，一个安全的系统需要 $n>300$，在这种情况下，私钥长度大于 $2n^2=180000\text{ bits}\approx 176\text{ KB}$（1KB=1024B）。这就太大了，以至于使安全的背包系统变得不切实际。

我们现在简要描述 Eve 如何使用向量来重新表述子集和问题。假设她想把 $S$ 写成集合 $M =(m_1,...,m_n)$ 的子集和。她的第一步是形成矩阵：

$$\begin{pmatrix}2& 0& 0 &\cdots& 0& m_1\\0& 2& 0 &\cdots& 0& m_2\\0& 0& 2 &\cdots& 0& m_3\\\vdots&\vdots&\vdots&\ddots&\vdots&\vdots\\0& 0& 0 &\cdots& 2& m_n\\1& 1& 1 &\cdots& 1& S\\\end{pmatrix}.\tag{*}$$

> 我把这个矩阵是称为 $(*)$ 矩阵是为了方便后面文章的叙述。

相关的向量是上面矩阵的行，她标记为：

$\begin{align}v_1&=(2,0,0,\dots,0,m_1),\\v_2&=(0,2,0,\dots,0,m_2),\\\vdots&\qquad\qquad\quad\vdots\\v_n&=(0,0,0,\dots,2,m_n),\\v_{n+1}&=(1,1,1,\dots,1,S).\\\end{align}\\$

与同余密码系统中考虑的 2 维示例类似，Eve 考虑 $v_1,\dots,v_{n+1}$ 所有整系数线性组合的集合，

$L=\{a_1v_1+a_2v_2+\dots+a_nv_n+a_{n+1}v_{n+1}:a_1,a_2,\dots,a_{n+1}\in \mathbb{Z}\}\\$

集合 $L$ 就是格的另一个例子。

假设 $x=(x_1,\dots,x_n)$ 是一个子集和问题的解，那么格 $L$ 包含向量：

$\begin{align}t&=\sum_{i=1}^nx_iv_i-v_{n+1}\\&=(2x_1,0,\dots,0,m_1x_1)+\dots+(0,0,\dots,2x_n,m_nx_n)-(1,1,\dots,1,S)\\&=(2x_1-1,2x_2-1,\dots,2x_n-1,0),\end{align}\\$

$t$ 的最后一个坐标为 $0$ 是因为 $S=x_1m_1+\dots+x_nm_n$。

我们现在进入了问题的关键部分。由于 $x_i$ 都是 0 或 1，所有的 $2x_i-1$ 值都是 $\pm1$，因此向量 $t$ 非常短，$\left\lVert t\right\rVert = \sqrt{n}$。另一方面，我们已经看到 $m_i = O(2^{2n})，S=O(2^{2n})$，所以生成 $L$ 的向量都有长度 $v_i = O(2^{2n})$。因此，除了 $t$ 之外，$L$ 不太可能包含任何长度小到 $\sqrt{n}$ 的非零向量。如果我们假设 Eve 知道一种算法，可以在格中找到短的非零向量，那么她将能够找到 $t$，从而恢复明文 $x$。

在格中寻找短向量的算法称为格约化算法（lattice reduction algorithms）。其中最著名的是我们之前提到的 LLL 算法及其变体,如 LLL-BKZ。



## 7.3 向量空间的简要回顾

> 这一节对应教材的 7.3.

向量空间有广义的定义，不过本章我们考虑在 $\mathbb{R}^m$ 上的向量空间。



**向量空间(Vector Spaces).** 一个向量空间 $V$ 是 $\mathbb{R}^m$ 的一个子集合，满足性质：

$\alpha_1 v_1+\alpha_2 v_2 \in V,\quad\text{for all}\ v_1,v_2 \in V \ \text{and all}\ \alpha_1,\alpha_2 \in \mathbb{R}\\$

即，一个向量空间 $V$ 是 $\mathbb{R}^m$ 的一个子集合，满足加法和取自 $\mathbb{R}$ 上元素的标量乘法封闭。



**线性组合(Linear Combinations).** 令 $v_1,v_2,\dots,v_k \in V$. $v_1,v_2,\dots,v_k \in V$ 的一个线性组合为一个有着如下形式的向量：

$w=\alpha_1 v_1+\alpha_2 v_2+\dots +\alpha_k v_k \quad with\ \alpha_1, \dots, \alpha_k \in \mathbb{R}\\$

所有这样的线性组合向量构成的集合：

$\{\alpha_1 v_1+\alpha_2 v_2+\dots +\alpha_k v_k :\ \alpha_1, \dots, \alpha_k \in \mathbb{R}\}\\$

称为 $\{v_1,v_2,\dots ,v_k \}$ 的一个扩张（span）.



**线性无关(Independence).** 称一组向量 $v_1,v_2,\dots,v_k \in V$ 是线性无关（linearly independent）当且仅当：

$\alpha_1 v_1+\alpha_2 v_2+\dots +\alpha_k v_k=0\\$

时，$\alpha_1=\alpha_2=\dots=\alpha_k=0$. 而线性相关则是上式成立时，至少有一个 $\alpha_i$ 非0.



**基底(Bases).** $V$ 的一个基底是一组线性无关向量 $v_1,v_2,\dots,v_n$ 能够扩张为整个 $V$. 即对于每一个向量 $w \in V$ , 都存在唯一的实数 $\alpha_1, \dots, \alpha_n \in \mathbb{R}$, 使得 $w$ 可以表示为：

$w=\alpha_1 v_1+\alpha_2 v_2+\dots +\alpha_n v_n\\$



**Proposition.** 令 $V \subset \mathbb{R}^m$ 是一个向量空间

1.  存在一个 $V$ 的基底
2.  $V$ 的任何两个基底都有相同数量的元素。基底中元素（向量）的个数称为向量空间的维数(dimension)
3.  令 $v_1,v_2,\dots,v_n$ 是 $V$ 的一个基底，$w_1,w_2,\dots,w_n$ 是 $V$ 中 $n$ 个向量。则 $w_j$ 可以写为 $v_i$ 的线性组合：  
    $w_1 = a_{11}v_1 + a_{12}v_2+\dots+a_{1n}v_n,\\w_2 = a_{21}v_1 + a_{22}v_2+\dots+a_{2n}v_n,\\\vdots \\w_n = a_{n1}v_1 + a_{n2}v_2+\dots+a_{nn}v_n,\\$  
    则 $w_1,w_2,\dots,w_n$ 也是 $V$ 的一组基当且仅当以下矩阵的行列式不等于0（因为$det(A)\neq0$说明向量$w_j$线性无关，并且$A$可以用向量$v_i$来进行表示）：  
    $\begin{pmatrix}{\alpha_{11}}&{\alpha_{12}}&{\cdots}&{\alpha_{1n}}\\{\alpha_{21}}&{\alpha_{22}}&{\cdots}&{\alpha_{2n}}\\{\vdots}&{\vdots}&{\ddots}&{\vdots}\\{\alpha_{n1}}&{\alpha_{n2}}&{\cdots}&{\alpha_{nn}}\\\end{pmatrix}\\$

下面我们将介绍如何衡量向量的长度（lengths） 和角度（angles）. 这与点积（dot product）和 Euclidean norm（即 $L_2$ 范式）有关.



**Definition.** 令 $v,w \in V \subset \mathbb{R}^m$, 并用坐标分别表示：

$v=(x_1,\dots,x_m)\ \text{and}\ w = (y_1, \dots, y_m)\\$

$v$ 与 $w$ 的内积为：

$v\cdot w = x_1y_1 + \dots+x_my_m\\$

我们说 $v$ 与 $w$ 是正交的（orthogonal）如果 $v\cdot w = 0$.

至于长度，或者说是 Euclidean norm 为：

$\left\lVert v \right\rVert = \sqrt{x^{2}_1+x^{2}_2+\dots +x^{2}_m}\\$

注意到点积和范数之间有以下关系：

$v\cdot v =\left\lVert v \right\rVert^2\\$



**Proposition.** 令 $v,w \in V \subset \mathbb{R}^m$.

1.  令 $\theta$ 表示 $v$ 与 $w$ 之间的角度。我们将向量 $v$ 和 $w$ 的起点放在原点 0，则  
    $v\cdot w =\left\lVert v \right\rVert \left\lVert w \right\rVert \cos(\theta)\\$
2.  (Cauchy-Schwarz 不等式)  
    $\lvert v\cdot w \rvert \leq \left\lVert v \right\rVert \left\lVert w \right\rVert \\$



**_Proof._** 命题 1 看简单的线性代数便可证明。当命题 1成立时，Cauchy-Schwarz 不等式立刻就能得到。但我们这里给出一个更直接的证明。

-   当 $w=0$ 时，直接成立，以下考虑 $w\neq 0$.
-   考虑函数：  
    $\begin{align}f(t) = \left\lVert v -tw\right\rVert^2 &=(v-tw)\cdot(v-tw)\\&=v\cdot v -2tv\cdot w +t^2 w\cdot w \\&=\left\lVert w\right\rVert^2 \cdot t^2 -2v\cdot w \cdot t +\left\lVert v \right\rVert^2\end{align}\\$  
    对于 $\forall t \in \mathbb{R}$, 都有$f(t) \geq 0$, 因此我们取其最小值, 即当 $t=\frac{v\cdot w}{\left\lVert w \right\rVert^2}$ 时：  
    $f(\frac{v\cdot w}{\left\lVert w \right\rVert^2})=\left\lVert v\right\rVert^2 - \frac{(v\cdot w)^2}{\left\lVert w \right\rVert^2} \geq 0\\$  
    化简后开根号，即可证得。



**Definition.** 一个向量空间 $V$ 的正交基（orthogonal basis）是一组基满足：

$v_i \cdot v_j = 0 \quad \forall i \neq j\\$

如果额外满足$\forall i,\ \left\lVert v_i \right\rVert=1$, 则称为标准正交基（orthonormal）.

当 $v_1, \dots, v_n$ 是正交基时，基的线性组合 $v = a_1v_1+\dots+a_nv_n$ 有如下性质：

$\begin{align}\left\lVert v \right\rVert^2 &= \left\lVert a_1v_1+\dots+a_nv_n \right\rVert^2\\&=(a_1v_1+\dots+a_nv_n)\cdot (a_1v_1+\dots+a_nv_n)\\&=\sum_{i=1}^n\sum_{j = 1}^n a_ia_j(v_i\cdot v_j)\\&=\sum_{i=1}^n a_i^2\left\lVert v_i \right\rVert^2\quad \text{since}\ v_i \cdot v_j = 0\ \text{for}\ i\neq j \end{align}\\$

若基底是标准正交基，则上式可化简为 $\left\lVert v \right\rVert^2 = \sum a_i^2$.

Gram-Schmidt 算法可以创造一个标准正交基，这里讨论通用算法的一个变体，相应给出的是正交基。



**Theorem (Gram-Schmidt Algorithm).** 令 $v_1, \dots, v_n$ 是向量空间 $V\subset \mathbb{R}^m$ 的一组基。下面算法可以构建 $V$ 的一个标准正交基 $v_1^*, \dots, v_n^*$：

![](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/v2-525681ffd66b74c06c7ac1ebdc616400_1440w.jpg)

图 5. Gram-Schmidt算法，源自《An Introduction to Mathematical Cryptography》


两个基底满足以下性质：

$\text{Span}\{v_1,\dots,v_i\} = \text{Span}\{v_1^*,\dots,v_i^*\}\quad \text{for all}\ i=1,\dots,n.\\$

> 注意对于格 $L$ 来说，Gram-Schmidt 算法生成的 $n$ 个正交基并不一定仍在 $L$ 中，即并不一定仍是格 $L$ 的基。这组基是由 $v_1, \dots, v_n$ 扩张成的向量空间的一组正交基。



_Proof._ 我们需要证明两件事：

-   新生成的基底相互正交
-   两组基底的扩张是相同的

1.  基的正交性利用**数学归纳法**来证明。假设 $v_1^*,\dots, v_{i-1}^*$ 是相互正交的，我们需要证明 $v_i^*$ 与前面所有带有"\*"的向量是正交的。对于 $k<i$（即$k\in [1,i-1]$）, 我们计算：  
    $\begin{align}v_i^* \cdot v_k^* &= \left(v_i - \sum_{j=1}^{i-1}\mu_{ij}v_j^* \right) \cdot v_k^*\\&=v_i \cdot v_k^* - \mu_{ij} \left\lVert v_k^* \right\rVert^2 &\quad \text{since}\ v_k^* \cdot v_j^* = 0 \ \text{for}\ j \neq k,\\&=0 &\quad \text{将}\ \mu_{ij}=v_i\cdot v^*_j/\lVert v_j^*\rVert^2 \quad \text{for} \quad 1\le j<i代入即可得到\end{align}\\$
2.  扩张本质是集合，而证明集合的相等我们只需证明**相互包含**即可。

-   $\subseteq$：根据 $v_i^*$ 的定义，我们可以将 $v_i$ 表示为：  
    $v_i = v_i^*+\sum_{j=1}^{i-1}\mu_{ij}v_j^*\\$  
    即 $v_i$ 可以被表示为 $v_i^*$ 的线性组合。于是有 $v_i \in \text{Span}\{v_1^*,\dots,v_i^*\}$. 即有 $\subseteq$
-   $\supseteq$：数学归纳法。假设 $v_1^*,\dots,v_{i-1}^*$ 属于 $\text{Span}\{v_1,\dots,v_{i-1}\}$. 我们需要证明 $v_i^{*} \in \text{Span}\{v_1,\dots,v_i\}$. 根据定义 $v_i^*=v_i - \sum_{j=1}^{i-1}\mu_{ij}v_j^*$, 则 $v_i^* \in \text{Span}\{v_1^*,\dots,v_{i-1}^*, v_i\}$（可以被线性表示）. 而 $v_1^*,\dots,v_{i-1}^*$ 属于 $\text{Span}\{v_1,\dots,v_{i-1}\}$，因此 $v_i^* \in \text{Span}\{v_1,\dots,v_{i-1}, v_i\}$，即有 $\supseteq$



## 7.4 格基：基本定义和性质

这一节我们正式开始介绍格的内容。

### 格的定义

**Definition.** 令 $v_1,\dots,v_n \in \mathbb{R}^m$ 是一组线性无关向量（$v_i$有$m$个维数）。由 $v_1, \dots,v_n$ 生成（generate）的格（lattice） $L$ 是 $v_1,\dots,v_n$ 的线性组合，其中系数取自 $\mathbb{Z}$,

$$
L = \{a_1v_1 + a_2v_2 + \dots + a_nv_n:\ a_1,a_2,\dots,a_n \in \mathbb{Z}\}.\\
$$
$L$ 的基是任何一组能够生成 $L$ 的线性无关的向量。任何两个基都有相同数量的元素。基中向量的个数称为格 $L$ 的维数（dimension）。

> 这里也会看到其他的定义方式，如 Oded Regev 的[课程笔记](https://cims.nyu.edu/~regev/teaching/lattices_fall_2004/)中，会将 **$m$ 称为格的维数（dimension）**，而 $n$ 称为格的秩(rank)。当 $n=m$ 时称格为满秩格(full rank lattice)。一般密码学中都是讨论满秩格。  
> 但在本书以及在 [Hermite’s Constant and Lattice Algorithms](https://www.di.ens.fr/~pnguyen/Nguyen_HermiteConstant.pdf) 的 Definition 6 中，都是把**基中向量的个数称为维数**。我个人倾向于认为 $n$ 应该是维数，因为类比线性空间中维数的定义，维数是基中向量的个数，那么 $L$ 的基中向量个数是 $n$，因此维数应该是 $n$。  
> $n$ 可以称为秩，这个没问题，因为格也可以用矩阵表示：  
> $L=\{Bx \vert x\in \mathbb{Z}^n\}.$  
> 其中 $B=(v_1,\dots,v_n)$ 是基底组成的 $m\times n$ 的矩阵。  
> 根据矩阵秩的定义可以得到 _秩=列秩=行秩=行/列向量的极大线性无关组中向量的个数=_ $n$。  
> 当然这只是个小问题。

设 $v_1,v_2,\dots,v_n$ 是 $V$ 的一个基底，$w_1,w_2,\dots,w_n$ 是 $V$ 中 $n$ 个向量。则 $w_j$ 可以写为基的线性组合：

$$
w_1 = a_{11}v_1 + a_{12}v_2+\dots+a_{1n}v_n,\\w_2 = a_{21}v_1 + a_{22}v_2+\dots+a_{2n}v_n,\\\vdots \\w_n = a_{n1}v_1 + a_{n2}v_2+\dots+a_{nn}v_n,\\
$$
由于是格，这里的系数都是整数。

我们在线性空间中研究过基变换，我们来看一下格中两个基的关系。分别令 $W, U$ 表示 $w_j$ 和 $v_i$ 两个列向量，$A$ 表示整系数矩阵：

$A=\begin{pmatrix}{a_{11}}&{a_{12}}&{\cdots}&{a_{1n}}\\{a_{21}}&{a_{22}}&{\cdots}&{a_{2n}}\\{\vdots}&{\vdots}&{\ddots}&{\vdots}\\{a_{n1}}&{a_{n2}}&{\cdots}&{a_{nn}}\\\end{pmatrix}\\$

则有 $W = A\cdot U$. 我们考虑利用 $w_j$ 来表示 $v_i$, 此时只需要对 $A$ 求逆便能得到 $U = A^{-1}\cdot W$. 在格中，线性组合的系数必须都是整数，所以 $A^{-1}$ 中的元素也一定均为整数。注意到：

$1 = \det(I) = \det(AA^{-1}) = \det(A)\cdot \det(A^{-1})\\$

而根据行列式的定义，整数矩阵的行列式一定是整数（行列式的定义为某行/列元素与其代数余子式的乘积再求和，只涉及到整数的加法和乘法，所以得到的结果一定是整数），于是 $\det(A), \det(A^{-1})$ 均为整数，从而只能得到$\det(A) = \pm 1$. 这就证明了如下结果：



**Proposition.** 格 $L$ 的任意两个基，其基变换矩阵中各元素均为整数，且行列式等于 $\pm 1$.

为了计算方便，我们经常会考虑向量坐标取自整数的格。例如：

$\mathbb{Z}^n=\{(x_1,x_2,\dots,x_n):\ x_1,x_2,\dots,x_n \in \mathbb{Z}\}\\$

为所有整数坐标的向量所构成的格。我们可以直观看一下 $\mathbb{Z}^2$ 上的格：

![](https://pic1.zhimg.com/v2-35567d5201c8066ffe4083ce201f99cc_1440w.jpg)

图 2. 格的一个实例



**Definition.** 一个整数格(integral or integer lattice)是指所有整数坐标的向量所构成的格。等价来说，一个整数格是加法群 $\mathbb{Z}^m$ 的一个子群，对$m\ge 1$。

__*Example.*__ 考虑由三个向量生成的格基$L\subset\mathbb{R}^3$

$$
\boldsymbol{v}_1=(2,1,3),\quad\boldsymbol{v}_2=(1,2,0),\quad\boldsymbol{v}_3=(2,-3,-5).
$$


使用$\boldsymbol{v}_1，\boldsymbol{v}_2，\boldsymbol{v}_3$作为矩阵的行来形成一个矩阵是很方便的。
$$
A=\begin{pmatrix}2&1&3\\1&2&0\\2&-3&-5\end{pmatrix}=\begin{pmatrix}\boldsymbol{v}_1\\ \boldsymbol{v}_2\\ \boldsymbol{v}_3\end{pmatrix}.
$$
我们通过以下公式在 $L$ 中创建三个新的向量
$$
\boldsymbol{w}_1=\boldsymbol{v}_1+\boldsymbol{v}_3,\quad\boldsymbol{w}_2=\boldsymbol{v}_1-\boldsymbol{v}_2+2\boldsymbol{v}_3,\quad\boldsymbol{w}_3=\boldsymbol{v}_1+2\boldsymbol{v}_2.
$$
相当于矩阵$A$左乘矩阵$U$

$$
U=\begin{pmatrix}1&0&1\\1&-1&2\\1&2&0\end{pmatrix}
$$
并且我们发现$\boldsymbol{w}_1、\boldsymbol{w}_2、\boldsymbol{w}_3$是该矩阵的行，即

$$
\begin{pmatrix}\boldsymbol{w}_1\\ \boldsymbol{w}_2 \\ \boldsymbol{w}_3\end{pmatrix}=UA=U\begin{pmatrix}\boldsymbol{v}_1\\ \boldsymbol{v}_2\\ \boldsymbol{v}_3\end{pmatrix}
$$

$$
B=UA=\begin{pmatrix}4&-2&-2\\5&-7&-7\\4&5&3\end{pmatrix}.
$$

矩阵$U$的行列式为-1，因此向量$\boldsymbol{w}_1、\boldsymbol{w}_2、\boldsymbol{w}_3$也是 $L$ 的一组基。$U$的逆矩阵是

$$
U^{-1}=\begin{pmatrix}&4&-2&-1\\&-2&1&1\\&-3&2&1\end{pmatrix},
$$
而 $U^{-1}$ 的行告诉我们如何将 $\boldsymbol{v}_i$ 表示为 $\boldsymbol{w}_j$ 的线性组合，因为
$$
\begin{pmatrix}\boldsymbol{v}_1\\ \boldsymbol{v}_2\\ \boldsymbol{v}_3\end{pmatrix}=U^{-1}\begin{pmatrix}\boldsymbol{w}_1\\ \boldsymbol{w}_2 \\ \boldsymbol{w}_3\end{pmatrix}
$$
所以 
$$
\boldsymbol{v}_1=4\boldsymbol{w}_1-2\boldsymbol{w}_2-\boldsymbol{w}_3,\quad\boldsymbol{v}_2=-2\boldsymbol{w}_1+\boldsymbol{w}_2+\boldsymbol{w}_3,\quad\boldsymbol{v}_3=-3\boldsymbol{w}_1+2\boldsymbol{w}_2+\boldsymbol{w}_3.
$$


**_Remark._** 如果 $L\subset \mathbb{R}^m$ 是一个 $n$ 维的格，则 $L$ 的一个基可以被写为 $n$ 行 $m$ 列的矩阵 $U$，设 $v_i = (u_{i1}, \dots, u_{im})$ 即有：

$U=(v_1, \dots,v_n)^T =\begin{pmatrix}{u_{11}}&{u_{12}}&{\cdots}&{u_{1m}}\\{u_{21}}&{u_{22}}&{\cdots}&{u_{2m}}\\{\vdots}&{\vdots}&{\ddots}&{\vdots}\\{u_{n1}}&{u_{n2}}&{\cdots}&{u_{nm}}\\\end{pmatrix}\\$

$L$ 的一个新的基底可以通过左乘一个 $n\times n$ 的矩阵 $A$ 来得到。$A$ 中元素均为整数且行列式为 $\pm1$ (这里其实就是重复了上面的那个命题).

格还有一种更为抽象的定义，其结合了几何与代数的理念。



**Definition.** $\mathbb{R}^m$ 的子集 $L$ 是一个加法子群，如果其对于加法和减法封闭。我们称 $L$ 是一个离散加法子群(discrete additive subgroup) 如果存在一个正数 $\epsilon > 0$, 对于所有的 $v \in L$ 满足如下性质：
$$
L \cap\{w \in \mathbb{R}^m:\ \left\lVert v-w \right\rVert < \epsilon\}=\{v\}.\\
$$
换句话说，如果在 $L$ 中取任意的一个向量 $v$，并在其周围做一个半径为 $\epsilon$ 的实心球，则球内除 $v$ 之外没有任何其他 $L$ 中的点。



**Theorem.** $\mathbb{R}^m$ 的一个子集是格当且仅当其是一个离散加法子群。

> 教材没有给出证明，以下证明为个人理解。

_Proof._ 充分性是容易证的，首先格 $L$ 是 $\mathbb{R}^m$ 的加法子群。又因为格中存在最短向量，只需要令 $\epsilon = \text{最短向量}$ 即可。必要性的证明从直观上想，根据离散加法子群的定义 $L$ 一定是由一些离散的点组成的，于是 $L$ 应该是一个格。

格与向量空间类似，不同之处在于格是由其基向量的所有整数系数线性组合生成的，而非任意实数系数的线性组合。将格视为 m 维实空间（$\mathbb{R}^m$）中有序排列的点集通常很有用，我们在每个向量的端点处放置一个点。下图 7.1 展示了二维$\mathbb{R}^2$中的一个格的例子。



### 基本域

**Definition.** 令 $L$ 为 $n$ 维格，$v_1,\dots,v_n$ 是 $L$ 的一个基。$L$ 在这组基下的基本域(fundamental domain/fundamental parallelepiped)是集合：
$$
\mathcal{F}(v_1,\dots,v_n)=\{t_1v_1+t_2v_2+\dots+t_nv_n:\ 0\leq t_i<1 \}\\
$$
下图展示了一个2维格上的基本域。

![image-20250912223525882](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250912223525882.png)

图 7.1 格与基本域，源自《An Introduction to Mathematical Cryptography》

下面的命题说明了基本域在学习格中的重要性。



**Proposition.** 设$L\subset \mathbb{R}^n$ 是 $n$ 维 格，令 $\mathcal{F}$ 是 $L$ 的基本域。则每一个向量 $w\in \mathbb{R}^n$ 都可以被写成如下形式：
$$
w = t+v\quad \text{for a unique}\ t \in \mathcal{F}\ \text{and a unique}\ v \in L\\
$$
等价来说，当 $v$ 遍历格 $L$ 中的向量时，平移后的基本域(the translated fundamental domains)的并集：

$$
\mathcal{F}+v = \{t+v:\ t \in \mathcal{F}\}\\
$$
恰好覆盖整个 $\mathbb{R}^n$. 下图展示了经过 $L$ 中的向量平移后的基本域 $\mathcal{F}$ 恰好覆盖了整个 $\mathbb{R}^n$.

![](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/20250913004124063.png)

图7.2 利用格中向量对基本域平移，源自《An Introduction to Mathematical Cryptography》


_Proof._ 令 $v_1,\dots,v_n$ 是 $L$ 的一个基，其生成的基本域为 $\mathcal{F}$. 则 $v_1,\dots,v_n$ 在 $\mathbb{R}^n$ 上线性无关，于是它们也是 $\mathbb{R}^n$ 的一个基。因此，任意的 $w\in \mathbb{R}^n$ 都能被写为形如：

$$
w = \alpha_1v_1+\alpha_2v_2+\dots+\alpha_nv_n \quad \text{for some}\ \alpha_1, \dots, \alpha_n \in \mathbb{R}.\\
$$
我们将每个 $\alpha_i$ 稍作变形：

$$
\alpha_i = t_i+a_i \quad \text{with}\ 0\leq t_i <1\ \text{and}\ a_i \in \mathbb{Z}\\
$$
从而将变形后的 $\alpha_i$ 代入原式得到：

$$
w = \overbrace{t_1v_1+t_2v_2+\dots+t_nv_n}^{\text{this is a vector}\ t \in \mathcal{F}}+\overbrace{a_1v_1+a_2v_2+\dots+a_nv_n}^{\text{this is a vector}\ v \in L}\\
$$
这便证得了 $w$ 可以被表示为我们想要的形式。但证明还没结束，下面我们还需要证明 $t$ 和 $v$ 的唯一性。证明唯一性通用的方法就是假设有两个，最后推出它们是相等的。

我们假设 $w = t+v=t^{'}+v^{'}$ 是其两种表示形式（$t^{'}$对应的的是$a^{'}$），则有：

$$
\begin{aligned}(t_1+a_1)v_1+(t_2+a_2)v_2+\dots+(t_n+a_n)v_n \\=(t_1^{'}+a_1^{'})v_1+(t_2^{'}+a_2^{'})v_2+\dots+(t_n^{'}+a_n^{'})v_n.\end{aligned}\\
$$
由于 $v_1,\dots,v_n$ 是相互独立的，所以有：

$$
t_i+a_i=t_i^{'}+a_i^{'}\quad \text{for all}\ i = 1,2,\dots,n.\\
$$
因此

$$
t_i-t_i^{'}=a_i^{'}-a_i \in \mathbb{Z}\\
$$
是一个整数。但 $t_i$ 和 $t_i^{'}$ 大于等于0且严格小于1，于是要想让 $t_i-t_i^{'}$ 是整数只能是 $t_i=t_i^{'}$， 因此 $t=t^{'}$. 并且：

$$
v=w-t=w-t^{'}=v^{'}\\
$$
这就完成了上述命题的完整证明。

基本域的体积(volume)是格中重要的一个不变量。



**Definition.** 设$L$ 是 $n$ 维 格，令 $\mathcal{F}$ 是 $L$ 的基本域。则 $\mathcal{F}$ 的 $n$ 维体积称为是 $L$ 的行列式(determinant) ，有时也被称为是协体积(covolume). 用 $\det(L)$ 来表示。

> 注意到格 $L$ 本身是没有体积的，因为它是一个可数点的集合。如果 $L$ 是包含在 $\mathbb{R}^n$ 中且其维度为 $n$，那么 $L$ 的协体积被定义为商群 $\mathbb{R}^n/L$ 的体积。

如果将基向量 $v_1,\dots,v_n$ 看作是描述基本域(parallelepiped) $\mathcal{F}$ 边长的给定长度的向量，那么对于给定长度的基向量，当这些向量两两正交时，所得到的体积(volume)是最大的。这导致了格的行列式有以下重要的上界：



**Proposition (Hadamard 不等式).** 令 $L$ 是一个 格，取 $L$ 任意的一组基 $v_1,\dots,v_n$, 且 $\mathcal{F}$ 是 $L$ 的一个基本域，则有
$$
\det(L) = \text{Vol}(\mathcal{F}) \leq \left\lVert v_1 \right\rVert \left\lVert v_2 \right\rVert \dots \left\lVert v_n \right\rVert\\
$$
基底越接近于正交，则 Hadamard 不等式越趋向于等式。即上式右侧部分表示基底正交时求得的体积。

> [行列式](https://link.zhihu.com/?target=https%3A//zh.wikipedia.org/wiki/%25E8%25A1%258C%25E5%2588%2597%25E5%25BC%258F)可以看作是有向面积或体积的概念在一般的(即更高维)欧几里得空间中的推广。**即矩阵的行列式可以解释为由其行（或列）向量张成的平行多面体的（定向的）体积**。这里我们可以通过2维和3维的小例子来感受一下这个不等式。  
> 2维以平行四边形和矩形为例。显然，当边相互正交时，面积最大，即同边长情况下，矩形的面积要大于平行四边形的面积，且当平行四边形的边趋近于垂直时，其面积也趋近于等于 $S_1$.  
> 3维以平行六面体和长方体为例。 考虑体积公式体积等于底面积乘高: $V=S\cdot h$, 在对应棱长相等的情况下，长方体的体积要大于平行六面体的体积。

![](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/v2-43243d2fb87b26bae1c45853b03eed4a_1440w.jpg)

2 维的一个例子

  

如果格 $L \in\mathbb{R}^n$ 中且 $L$ 的维数为 $n$, 那么计算格 L 的行列式就相对容易。下一个命题描述了这个公式，这种情况也是我们最感兴趣的。



**Proposition.** 设 $L \subset\mathbb{R}^n$ 是 $n$ 维格，令 $v_1,\dots,v_n$ 是 $L$ 的一组基，$\mathcal{F} = \mathcal{F}(v_1,\dots,v_n)$ 是相对应的基本域。用坐标表示第 $i$ 个基向量：
$$
v_i = (r_{i1}, r_{i2},\dots, r_{in})\\
$$
将向量 $v_i$ 的坐标作为矩阵的行向量,

$$
F=F(v_1,\dots,v_n)=\begin{pmatrix}{r_{11}}&{r_{12}}&{\cdots}&{r_{1n}}\\{r_{21}}&{r_{22}}&{\cdots}&{r_{2n}}\\{\vdots}&{\vdots}&{\ddots}&{\vdots}\\{r_{n1}}&{r_{n2}}&{\cdots}&{r_{nn}}\\\end{pmatrix}.\quad(7.11)\\
$$
则 $\mathcal{F}$ 的体积由下面的公式给出：

$$
\text{Vol}(\mathcal{F}(v_1,\dots,v_n))=\left\lvert \det(F(v_1,\dots,v_n))\right\rvert.\\
$$

> 对于一般情况，即非满秩格，其体积表示为 $\det{L} = \sqrt{\det(BB^{T})}$.

_**Proof.**_ 需要用到对多变量的积分，我们可以通过对区域 $\mathcal{F}$ 上的常数函数1进行积分来计算 $\mathcal{F}$ 的体积：
$$
\mathrm{Vol}(\mathcal{F})=\int_{\mathcal{F}}dx_1dx_2\cdots dx_n.
$$
基本域$\mathcal{F}$是由之前定义所描述的集合，因此我们根据以下公式将变量从$\boldsymbol{x}=(x_1,\ldots,x_n)$转化成$\boldsymbol{t}=(t_1,\ldots,t_n)$

$$
(x_1,x_2,\ldots,x_n)=t_1\boldsymbol{v}_1+t_2\boldsymbol{v}_2+\cdots+t_n\boldsymbol{v}_n.
$$
关于由式（7.11）定义的矩阵$F=F(v_1,\dots,v_n)$，变量替换由矩阵方程$x=\boldsymbol{t}F$给出。该变量替换的雅可比矩阵为$F$，基本域$\mathcal{F}$是单位立方体$C_n=[0,1]^n,$在$F$作用下的像，因此积分的变量替换公式可得
$$
\begin{gathered}\int_{\mathcal{F}}dx_{1}dx_{2}\cdots dx_{n}=\int_{FC_{n}}dx_{1}dx_{2}\cdots dx_{n}=\int_{C_{n}}|\operatorname*{det}F|dt_{1}dt_{2}\cdots dt_{n}\\=|\det F|\operatorname{Vol}(C_{n})=|\det F|.\end{gathered}
$$


_Example._ 考虑由如下三个线性无关向量生成的3维格 $L\subset \mathbb{R}^3$：

$v_1=(2,1,3),\ v_2 = (1,2,0),\ v_3=(2,-3,-5).\\$

则有：

$F(v_1,v_2,v_3)=\begin{pmatrix}2&1&3\\1&2&0\\2&-3&-5\\\end{pmatrix}.\\$

因此，格的体积为：

$\det(L) = \left\lvert\det(F) \right\rvert = 36\\$

**Corollary.（推论）** 设 $L \subset\mathbb{R}^n$ 是 $n$ 维 lattice，则 $L$ 的每一个基本域都有相同的体积。因此 $\det(L)$ 是格 $L$ 的不变量。

_Proof._ 令 $v_1,\dots,v_n$ 和 $w_1,\dots,w_n$ 分别生成了 $L$ 的两个基本域，并令 $F(v_1,\dots,v_n)$ 和 $F(w_1,\dots,w_n)$ 是与之相关联的矩阵。根据前面的命题，两个基做转换只需对其中一个基左乘一个行列式为 $\pm1$ 的 $n\times n$ 的矩阵 $A$ 即可。

$F(v_1,\dots,v_n)=AF(w_1,\dots,w_n)\\$

$v_1,\dots,v_n$ 生成的基本域的体积为：

$\begin{aligned}\text{Vol}(\mathcal{F}(v_1,\dots,v_n))&=\left\lvert \det(F(v_1,\dots,v_n)) \right\rvert\\&=\left\lvert \det(AF(w_1,\dots,w_n)) \right\rvert\\&=\left\lvert \det(A) \right\rvert \left\lvert \det(F(w_1,\dots,w_n)) \right\rvert\\&=\left\lvert \det(F(w_1,\dots,w_n)) \right\rvert\\&=\text{Vol}(\mathcal{F}(w_1,\dots,w_n))\end{aligned}\\$
