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

$$
A=\begin{pmatrix}{a_{11}}&{a_{12}}&{\cdots}&{a_{1n}}\\{a_{21}}&{a_{22}}&{\cdots}&{a_{2n}}\\{\vdots}&{\vdots}&{\ddots}&{\vdots}\\{a_{n1}}&{a_{n2}}&{\cdots}&{a_{nn}}\\\end{pmatrix}\\
$$
则有 $W = A\cdot U$. 我们考虑利用 $w_j$ 来表示 $v_i$, 此时只需要对 $A$ 求逆便能得到 $U = A^{-1}\cdot W$. 在格中，线性组合的系数必须都是整数，所以 $A^{-1}$ 中的元素也一定均为整数。注意到：

$1 = \det(I) = \det(AA^{-1}) = \det(A)\cdot \det(A^{-1})\\$

而根据行列式的定义，整数矩阵的行列式一定是整数（行列式的定义为某行/列元素与其代数余子式的乘积再求和，只涉及到整数的加法和乘法，所以得到的结果一定是整数），于是 $\det(A), \det(A^{-1})$ 均为整数，从而只能得到$\det(A) = \pm 1$. 这就证明了如下结果：



**Proposition 7.14** 格 $L$ 的任意两个基，其基变换矩阵中各元素均为整数，且行列式等于 $\pm 1$.

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
$$
U=(v_1, \dots,v_n)^T =\begin{pmatrix}{u_{11}}&{u_{12}}&{\cdots}&{u_{1m}}\\{u_{21}}&{u_{22}}&{\cdots}&{u_{2m}}\\{\vdots}&{\vdots}&{\ddots}&{\vdots}\\{u_{n1}}&{u_{n2}}&{\cdots}&{u_{nm}}\\\end{pmatrix}\\
$$
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
下图展示了一个2维格上的基本域，其实基本域就是下面阴影部分中的任何一条从原点出发的向量。

![image-20250912223525882](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20250912223525882.png)

图 7.1 格与基本域，源自《An Introduction to Mathematical Cryptography》

下面的命题说明了基本域在学习格中的重要性。



**Proposition 7.18.** 设$L\subset \mathbb{R}^n$ 是 $n$ 维格，令 $\mathcal{F}$ 是 $L$ 的基本域。则每一个向量 $w\in \mathbb{R}^n$ 都可以被写成如下形式：
$$
w = \boldsymbol{t}+\boldsymbol{v}\quad \text{对一个独一无二的}\ \boldsymbol{t} \in \mathcal{F}\ \text{和一个独一无二的}\ \boldsymbol{v} \in L\\
$$
等价来说，当 $\boldsymbol{v}$ 遍历格 $L$ 中的向量时，平移后的基本域(the translated fundamental domains)的并集：

$$
\mathcal{F}+\boldsymbol{v}= \{\boldsymbol{t}+\boldsymbol{v}:\boldsymbol{t} \in \mathcal{F}\}\\
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



**Proposition 7.19 (Hadamard 不等式).** 令 $L$ 是一个 格，取 $L$ 任意的一组基 $v_1,\dots,v_n$, 且 $\mathcal{F}$ 是 $L$ 的一个基本域，则有
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



**Proposition 7.20** 设 $L \subset\mathbb{R}^n$ 是 $n$ 维格，令 $v_1,\dots,v_n$ 是 $L$ 的一组基，$\mathcal{F} = \mathcal{F}(v_1,\dots,v_n)$ 是相对应的基本域。用坐标表示第 $i$ 个基向量：
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
基本域 $\mathcal{F}$ 是由之前定义所描述的集合，因此我们根据以下公式将变量从 $\boldsymbol{x}=(x_1,\ldots,x_n)$转化成 $\boldsymbol{t}=(t_1,\ldots,t_n)$

$$
(x_1,x_2,\ldots,x_n)=t_1\boldsymbol{v}_1+t_2\boldsymbol{v}_2+\cdots+t_n\boldsymbol{v}_n.
$$
关于由式（7.11）定义的矩阵$F=F(v_1,\dots,v_n)$，变量替换由矩阵方程$x=\boldsymbol{t}F$给出。该变量替换的雅可比矩阵为$F$，基本域$\mathcal{F}$是单位立方体$C_n=[0,1]^n,$在$F$作用下的像，因此积分的变量替换公式可得
$$
\begin{gathered}\int_{\mathcal{F}}dx_{1}dx_{2}\cdots dx_{n}=\int_{FC_{n}}dx_{1}dx_{2}\cdots dx_{n}=\int_{C_{n}}|\operatorname*{det}F|dt_{1}dt_{2}\cdots dt_{n}\\=|\det F|\operatorname{Vol}(C_{n})=|\det F|.\end{gathered}
$$


_Example._ 考虑由如下三个线性无关向量生成的3维格 $L\subset \mathbb{R}^3$：

$$
v_1=(2,1,3),\ v_2 = (1,2,0),\ v_3=(2,-3,-5).\\
$$
则有：

$$
F(v_1,v_2,v_3)=\begin{pmatrix}2&1&3\\1&2&0\\2&-3&-5\\\end{pmatrix}.\\
$$
因此，格的体积为：

$$
\det(L) = \left\lvert\det(F) \right\rvert = 36\\
$$


**Corollary.（推论）** 设 $L \subset\mathbb{R}^n$ 是 $n$ 维 格，则 $L$ 的每一个基本域都有相同的体积。因此 $\det(L)$ 是格 $L$ 的不变量。



**_Proof._** 令 $v_1,\dots,v_n$ 和 $w_1,\dots,w_n$ 分别生成了 $L$ 的两个基本域，并令 $F(v_1,\dots,v_n)$ 和 $F(w_1,\dots,w_n)$ 是与之相关联的矩阵。根据前面的命题7.14，两个基做转换只需对其中一个基左乘一个行列式为 $\pm1$ 的 $n\times n$ 的矩阵 $A$ 即可。
$$
$F(v_1,\dots,v_n)=AF(w_1,\dots,w_n) \quad (7.12)
$$
由命题7.20知 $v_1,\dots,v_n$ 生成的基本域的体积为：

$$
\begin{aligned}\text{Vol}(\mathcal{F}(v_1,\dots,v_n))&=\left\lvert \det(F(v_1,\dots,v_n)) \right\rvert\\&=\left\lvert \det(AF(w_1,\dots,w_n)) \right\rvert\\&=\left\lvert \det(A) \right\rvert \left\lvert \det(F(w_1,\dots,w_n)) \right\rvert\\&=\left\lvert \det(F(w_1,\dots,w_n)) \right\rvert\\&=\text{Vol}(\mathcal{F}(w_1,\dots,w_n))\end{aligned}\\
$$


## 7.5 格中的最短向量


格最基本的计算困难问题为寻找格中最短的非零向量和给定一个不在格中的向量，寻找一个与之最近的向量。这一节我们主要从理论上来讨论这些问题。

> 不过在讨论最短向量问题之前，首先应该证明格中最短向量的存在性。**格的离散性保证了长度最短的非零向量的存在性**\[1\]。至于再严格的证明我也真的没有找到。。。  
> 格的离散性(discret)是指：每个点 $x\in\mathbb{Z}^n$ 在 $\mathbb{R}^n$ 中都存在一个邻域，在该邻域内 $x$​ 是唯一的格点。\[2\]

###  7.5.1 最短向量问题和最近向量问题

我们首先对两个格上的基本问题进行讨论。

**最短向量问题(The Shortest Vector Problem, SVP):** 寻找一个非零格向量 $v$，使得 Euclidean norm $\left\lVert v\right\rVert$ （欧几里得范数）最小。

**最近向量问题(The Closest Vector Problem, CVP):** 给定一个不在 $L$ 中的向量 $w\in \mathbb{R}^m$，寻找一个格中的向量 $v\in L$，使得 Euclidean norm $\left\lVert w-v\right\rVert$ 最小。



_Remark 7.23_ 注意，格中的最短非零向量不止一个，例如在 $\mathbb{Z}^2$ 中，$(0,\pm1), (\pm1,0)$ 这四个向量都是 SVP 的解。这就是为什么最短向量问题要求的是”一个“最短向量，而不是“那个”最短向量。CVP同理。

SVP 和 CVP 属于计算上的困难问题。此外，即使是 SVP 和 CVP 的近似解，在纯数学或者应用数学的不同领域也有很多有趣的应用。在计算复杂性框架下，SVP 在随机归约假设(randomized reduction hypothesis)下是 $\mathcal{NP}$\-hard，而精确的 CVP 是 $\mathcal{NP}$\-hard.

> This hypothesis means that the class of polynomial-time algorithms is enlarged to include those that are not deterministic, but will, with high probability, terminate in polynomial time with a correct result. (教材小注)

在实际中，CVP 被认为比 SVP 稍难一点，因为 CVP 经常能够被归约到稍微更高维度(a slightly higher dimension)的 SVP。下面我们介绍 SVP 和 CVP 的几个重要的变体。

**最短基问题(Shortest Basis Problem, SBP):** 寻找格的一个基底 $v_1,\dots,v_n$ 使得在某种意义下是最短的。例如，我们可能会要求：

$$
\max_{1\leq i \leq n} \left\lVert v_i\right\rVert\quad \text{or}\quad \sum_{i=1}^n \left\lVert v_i\right\rVert^2\\
$$
最小。因此 SBP 有很多不同的版本，这取决于我们如何衡量一组基的“大小(size)”。

**近似最短向量问题(Approximate Shortest Vector Problem, apprSVP):** 令 $\psi(n) \geq 1$ 是 $n$ 的一个函数。在 $n$ 维格 $L$ 中，寻找一个非零向量，它的长度不会超过最短非零向量长度的 $\psi(n)$ 倍。即，令 $v_{\text{shortest}}$ 表示 $L$ 中的最短非零向量，寻找非零向量 $v\in L$ 满足：
$$
\left\lVert v\right\rVert \leq \psi(n) \left\lVert v_{\text{shortest}}\right\rVert.\\
$$
对 $\psi(n)$ 的不同选择会得到不同的 apprSVP。例如：

$$
\left\lVert v\right\rVert \leq 3\sqrt{n}\left\lVert v_\text{shortest}\right\rVert \quad \text{or} \quad \left\lVert v\right\rVert \leq 2^{n/2} \left\lVert v_\text{shortest}\right\rVert\\
$$
显然能够解决前一个问题的算法，也能被用来解决后一个问题。

**近似最近向量问题(Approximate Closest Vector Problem, apprCVP):** 令 $\psi(n) \geq 1$ 是 $n$ 的一个函数。给定一个向量 $w\in \mathbb{R}^m$，寻找一个非零格向量 $v\in L$ 使得：

$\left\lVert v-w\right\rVert \leq \psi(n)\cdot \text{dist}(w, L).\\$

其中，$\text{dist}(w,L)$ 表示 $w$ 与格 $L$ 中最近的向量之间的 Euclidean 距离。



### 7.5.2 Hermite定理和Minkowski定理

格中最短非零向量的长度，在一定程度上取决于格 $L$ 的维数(dimension)和行列式(determinant)。下面的定理给出了我们一个显式的上界。



**Theorem 7.25 (Hermite's Theorem).** 每一个维数为 $n$ 的格均包含了一个非零向量 $v\in L$ 满足：
$$
\left\lVert v\right\rVert \leq \sqrt{n} \det(L) ^{1/n}.\\
$$
_Remark 7.26_ 对于给定的维数 $n$，Hermite 常数(Hermite's constant) $\gamma_n$ 是一个最小值，表示使得任何 $n$ 维的格 $L$，都包含一个满足下式的非零向量 $v\in L$

$$
\left\lVert v\right\rVert^2 \leq \gamma_n \det(L) ^{2/n}.\\
$$
根据定理7.25我们可以得到 $\gamma_n \leq n$. 而对于 $\gamma_n$ 的准确值我们只知道 $1\leq n \leq 8$ 和 $n=24$ 的情况：

$$
\gamma_2^2=\frac{4}{3},\quad \gamma_3^3=2,\quad\gamma_4^4=4,\quad,\gamma_5^5=8,\quad\gamma_6^6=\frac{64}{3},\quad\gamma_7^7=64,\quad\gamma_8^8=256\\
$$
以及 $\gamma_{24}=4$.

在密码学中，我们主要对 $\gamma_n$ 和 $n$ 比较大的时候感兴趣。当 $n$ 很大时， Hermite 常数满足：

$$
\frac{n}{2\pi e} \leq \gamma_n \leq \frac{n}{\pi e},\\
$$
其中 $\pi=3.14159\dots$，$e=2.71828\dots$ 都是一般的常数。

_Remark 7.27._ Hermite 定理有很多版本，能够处理不止一个向量的情形。例如，我们可以证明一个 $n$ 维的格 $L$ 总有一组基$v_1,\ldots,v_n$满足：

$$
\left\lVert v_1\right\rVert\left\lVert v_2\right\rVert\dots\left\lVert v_n\right\rVert\leq n^{n/2}(\det(L))\\
$$

> 这个证明我能想到的就是利用 Minkowski 第二定理来直接得到，Minkowski 定理将在后面介绍

结合 Hadamard 不等式（定义7.19）：$\left\lVert v_1\right\rVert\left\lVert v_2\right\rVert\dots\left\lVert v_n\right\rVert \geq \det(L)$，可以得到：

$$
\frac{1}{\sqrt{n}} \leq \left( \frac{\det(L)}{\left\lVert v_1\right\rVert\left\lVert v_2\right\rVert\dots\left\lVert v_n\right\rVert}\right)^{1/n} \leq 1\\
$$
定义基底 $\mathcal{B}=\{v_1,\dots,v_n\}$ 的 Hadamard 比率(Hadamard ratio)为：

$$
\mathcal{H}(\mathcal{B})=\left( \frac{\det(L)}{\left\lVert v_1\right\rVert\left\lVert v_2\right\rVert\dots\left\lVert v_n\right\rVert}\right)^{1/n}\\
$$
因此 $0<\mathcal{H}(\mathcal{B})\leq 1$，且比值越接近于1，基底向量越趋向于正交(其实就是 Hadamard 不等式的结论)。Hadamard 比率的倒数有时被称为正交性缺陷(orthogonality defect)。

Hermite 定理的证明利用了 Minkowski 定理，我们将在后面介绍。为了介绍 Minkowski 定理，我们引入一个有用的符号表示法并给出一些基本定义。



**Definition.** 对于任意的 $a \in \mathbb{R}^n$ 和任意的 $R >0$，以 $a$ 为中心，半径为 $R$ 的(闭)球(closed ball)是集合：

$$
\mathbb{B}_R(a)=\{x\in \mathbb{R}^n:\ \left\lVert x-a\right\rVert\leq R\}.\\
$$




**Definition.** 令 $S$ 是 $\mathbb{R}^n$ 的一个子集。

1.  $S$ 是有界的(bounded)，如果 $S$ 中的向量长度是有界的。即如果存在一个半径 $R$，使得 $S$ 被包含在球 $\mathbb{B}_R(0)$中，则称 $S$ 有界。
2.  $S$​ 是对称的(symmetric)，如果对于 $S$​ 中的每个点 $a$​，则其逆 $-a$​ 也在 $S$​ 中。
3.  $S$ 是[凸的(convex)](https://zh.wikipedia.org/wiki/凸集)，如果 $S$ 中的任意两点 $a$ 和 $b$ 满足，连接 $a$ 和 $b$ 的整个线段点完全位于 $S$ 内。
4.  $S$ 是[闭的(closed)](https://zh.wikipedia.org/wiki/%E9%97%AD%E9%9B%86)，如果对于点 $a\in \mathbb{R}^n$ 满足，每个以 $a$ 为中心、半径为 $R$ 的球 $\mathbb{B}_R(a)$ 都包含 $S$ 中的点，则 $a$ 属于 $S$。

> 闭集合另一个比较好理解的等价定义是：**一个集合为闭集当且仅当它包含其自身所有的极限点**。极限点是指：对于任意小的正半径 $R$ ，以 $a$ 为中心的球 $\mathbb{B}_R(a)$ 内总是存在 $S$ 中的点。  
> 上面的定义可以在2维或3维上举个例子帮助理解。超链接中给出了维基百科的定义，其中有一些例子也可以帮助理解。

[Minkowski 定理](https://en.wikipedia.org/wiki/Minkowski's_theorem)告诉我们：如果 $\mathbb{R}^n$ 中的一个关于原点对称的凸几何体 $S$ 的体积大于 $2^n$，那么 $S$ 必包含一个非原点的整数点。这个定理可以从整数格扩展到任意的格中。



**Theorem 7.28 (Minkowski's Theorem).** 设 $L \subset \mathbb{R}^n$ 是一个 $n$ 维的格，令 $S \subset \mathbb{R}^n$ 是一个对称凸集合(symmetric convex set)，其体积(volume)满足：
$$
\text{Vol}(S) > 2^n\det(L).\\
$$
则 $S$ 包含一个非零的格向量。如果 $S$ 同时也是闭的，则条件可以放宽到 $\text{Vol}(S) \geq 2^n\det(L).$​

> 定理也被称为 Minkowski 凸体定理(Minkowski convex body theorem)。

_Proof._ 令 $\mathcal{F}$ 表示 $L$ 的基本域。我们在基本域一节（定义7.18）已经讨论过，对于任意 $a\in S$，都能被唯一的表示为：

$$
a=v_a+w_a\quad \text{with}\ v_a\in L\ \text{and}\ w_a \in \mathcal{F}.\\
$$
我们令 $S^{'} = \frac{1}{2}S$，即将 $S$ 缩小两倍：

$$
S^{'}=\frac{1}{2}S=\left\{\frac{1}{2}a:\ a\in S\right\}\\
$$
考虑映射：

$$
\begin{align}f:\ & \frac{1}{2}S \rightarrow \mathcal{F},\\&\frac{1}{2}a \mapsto w_{\frac{1}{2}a}.\end{align}\\
$$
将 $S$ 缩小 2 倍会使其体积变为原来的 $1/2^n$，于是：

$$
\text{Vol}(\frac{1}{2}S)=\frac{1}{2^n}\text{Vol}(S) > \det(L) = \text{Vol}(\mathcal{F}).\\
$$
这里我们利用了假设 $\text{Vol}(S)>2^n \det(L)$。

> 对于一个 $n$ 维空间中的集合 $S$ ，如果我们对每一个点进行缩放，即将每一个点 $x\in S$ 缩放到 $cx$，其中 $c$ 是一个标量，那么新的集合 $cS$ 的体积 $V(cS)$ 与原集合 $S$ 的体积 $V(S)$ 之间的关系是： $$$V(cS)=|c|^nV(S)$$$

映射 $f$ 由有限个平移映射([translation map](https://proofwiki.org/wiki/Definition:Translation_Mapping))组成(这里使用了 $S$ 有界的假设)，因此该映射是保持体积的。定义域 $S^{'}$ 的体积严格大于值域 $\mathcal{F}$ 的体积，意味着存在不同的点 $\frac{1}{2}a_1$ 和 $\frac{1}{2}a_2$，映射到了 $\mathcal{F}$ 中相同的像：

$$
\frac{1}{2}a_1=v_1+w\quad \text{and} \quad \frac{1}{2}a_2=v_2 + w \quad\text{with}\ v_1,v_2\in L\ \text{and}\ w \in \mathcal{F}.\\
$$

> $S, S^{'}, \mathcal{F}$ 都是 $\mathbb{R}^n$ 的子集合，那么映射 $f$ 相当于是将在 $S^{'}$ 中的那些点/向量给_平移_ 到了 $\mathcal{F}$ 中，本质其实都是在 $\mathbb{R}^n$ 中移动点。因此经过有限次的平移后，这些点所构成的体积应该是不变的，即保持体积。  
> 但现在经过映射后，反而体积变小了，这说明 $f$ 不是一个单射，否则应该有  
> $f(S^{'}) \subset \mathcal F \Rightarrow \text{Vol}(S^{'})=\text{Vol}(f(S^{'})) \leq \text{Vol}(\mathcal{F})$

![](https://pic2.zhimg.com/v2-d6b9aba023e1a2ba63ae5d6c969925c9_1440w.jpg)

> 但这就与我们的假设 $\text{Vol}(S)>2^n \det(L)$ 矛盾了，因此有 $S^{'}$ 中不同的原像映射到了相同的 $\mathcal{F}$ 中的像。

![](https://pica.zhimg.com/v2-f3c2805551d243ce5aa6317bd87808f6_1440w.jpg)

两式相减得到非零向量：

$$
\frac{1}{2}a_1-\frac{1}{2}a_2=v_1-v_2 \in L.\\
$$
同时：

$$
\underbrace{\frac{1}{2}a_1+\overbrace{(-\frac{1}{2}a_2)}}^{S\text{ is sysmetric, }\text{so } -a_2 \text{ is in } S}_{\begin{align}\text{this is the midpoint of the line}\\\text{ segment from }a_1\ \text{to}\ -a_2,\ \ \ \\ \text{so it is in}\ S\ \text{by convexity}\ \ \ \end{align}}\in S\\
$$
因此：

$$
0 \neq v_1 -v_2 \in S\cap L,\\
$$
于是我们在 $S$ 中构建了一个非零格点。

_Proof of Hermite's theorem._ 设 $L \subset \mathbb{R}^n$ 是一个 lattice，令 $S$ 表示 $\mathbb{R}^n$ 上的以0为中心，边长长为 $2B$ 的一个超方形 ([hypercube](https://link.zhihu.com/?target=https%3A//zh.wikipedia.org/wiki/%25E8%25B6%2585%25E6%2596%25B9%25E5%25BD%25A2))，

$S=\{(x_1,\dots,x_n)\in \mathbb{R}^n:\ -B \leq x_i\leq B \quad \text{for all }1 \leq i \leq n\}.\\$

集合 $S$ 满足对称性、封闭性且有界，其体积为：

$\text{Vol}(S) = (2B)^n\\$

因此，如果我们令 $B=\det(L)^{1/n}$，则 $\text{Vol}(S)=2^n\det(L)$，此时应用 Minkowski 定理便能推导出存在一个非零向量 $0\neq a \in S \cap L$。用坐标表示 $a=(a_1,\dots,a_n),\ -B \leq a_i\leq B$，根据 $S$ 的定义我们有：

$\left\lVert a \right\rVert = \sqrt{a_1^2+\dots+a_n^2} \leq \sqrt{n}B = \sqrt{n} \det(L)^{1/n}.\\$

这就完成了 Hermite 定理的证明。

> 这里补充一下格的逐次最小长度(successive minima) 与 Minkowski 第一第二定理。  
> 参考论文：格的计算和密码学应用，并将符号与本书做了下统一。  
> **Definition.** 令 $L$ 是 $n$ 维格，对于 $i\in\{1,\dots,n\}$，我们定义第 $i$ 个逐次最小长度 $\lambda_i(L)$ 为包含 $i$ 个线性无关的格向量的以原点为球心的球的最小半径，即  
> $\lambda_i(L)=\min\{r>0:\dim(\text{Span}(L\cap\mathbb{B}_r(0)))\geq i\},$  
> 特别地，$\lambda_1(L)$ 是格 $L$ 中最短非零向量的长度。下面两个结果分别被称为 Minkowski 第一和第二定理.  
> **Theorem.** 对于任意 $n$ 维格 $L$，有  
> $1. \ \lambda_1(L) < \sqrt{n}\det(L)^{\frac{1}{n}}$；  
> $2.\ \prod_{i=1}^n\lambda_i(L)^{\frac{1}{n}}<\sqrt{n}\det(L)^{\frac{1}{n}}$.

### 7.5.3 Gaussian 启发式

通过将 Minkowski 定理应用于超球面([hypersphere](https://link.zhihu.com/?target=https%3A//zh.wikipedia.org/wiki/N%25E7%25BB%25B4%25E7%2590%2583%25E9%259D%25A2))，而不是超立方体(hypercube),可以改进出现在 Hermite 定理中的常数。为了实现这一点，我们需要知道在 $\mathbb{R}^n$ 中球体的体积。

**Definition.** 对于 $s>0$，伽马函数(gamma function) $\Gamma(s)$ 用积分定义为：

$\Gamma(s)=\int_0^{\infty} t^s e^{-t}\frac{dt}{t}.\\$

我们列出一些基本性质。

**Proposition.**

1.  对于所有的 $s>0$，定义 gamma 函数 $\Gamma(s)$ 的积分是收敛的。
2.  $\Gamma(1)=1$ 且 $\Gamma(s+1)=s \Gamma(s)$。这使得我们能够将 $\Gamma(s)$ 扩展到所有 $s \in \mathbb{R}$ 上，对于 $s\neq 0,-1,-2,\dots$.
3.  对于所有的整数 $n\geq 1$，我们有 $\Gamma(n+1)=n!$。因此 gamma 函数即为阶乘函数在实数与复数域上的推广。
4.  $\Gamma(\frac{1}{2})=\sqrt{\pi}$​.
5.  (Stirling's 公式) 当 $s$ 很大时我们有：  
    $\Gamma(1+s)^{1/s}\approx\frac{s}{e}.\\$  
    更精确来说，  
    $\ln\Gamma(1+s)=\ln(\frac{s}{e})^s+\frac{1}{2}\ln(2\pi s) +O(1)\ \text{as } s \rightarrow \infty.\\$

$n$ 维空间中的球体体积公式包含了 gamma 函数。

**Theorem.** 令 $\mathbb{B}_R(a)$ 表示 $\mathbb{R}^n$ 中半径为 $R$ 的球体。则其体积为：

$\text{Vol}(\mathbb{B}_R(a))=\frac{\pi^{n/2}R^n}{\Gamma(1+\frac{n}{2})}.\\$

当 $n$ 很大时，利用Stirling公式和上式可以得到，$\mathbb{B}_R(a)$ 的体积可以近似表示为：

$\text{Vol}(\mathbb{B}_R(a))^{1/n}\approx\sqrt{\frac{2\pi e}{n}}R.\\$

_Remark._ 利用上面的定理我们可以改进 Hermite 定理当 $n$ 很大时的情况。球体 $\mathbb{B}_R(0)$ 是有界的、封闭的、凸的且对称的，于是根据 Minkowski 定理，如果我们选择 $R$ 满足：

$\text{Vol}(\mathbb{B}_R(0)) \geq 2^n \det(L),\\$

则球体 $\mathbb{B}_R(0)$ 包含了一个非零格点。当 $n$ 很大时，利用球体体积的近似公式，我们需要选择 $R$ 满足：

$\sqrt{\frac{2\pi e}{n}}R \gtrapprox 2\det(L)^{1/n}\\$

根据 $\mathbb{B}_R(0)$ 的定义，有：

$\mathbb{B}_R(0)=\{x \in \mathbb{R}^n:\ \left\lVert x \right\rVert \leq R\}\\$

因此，存在一个非零向量 $v \in L$​ 满足：

$\left\lVert v \right\rVert\lessapprox\sqrt{\frac{2n}{\pi e}} \cdot (\det(L))^{1/n}\\$

这便通过一个因子 $\sqrt{2/\pi e} \approx 0.484$ 改进了 Hermite 定理。

尽管最短向量的准确界在 $n$ 很大时是未知的，但我们可以基于以下原理的概率论证来估计其范围：

> 令 $\mathbb{B}_R(0)$ 是以 0 为中心的大球体。则 $\mathbb{B}_R(0)$ 内的格点数约等于 $\mathbb{B}_R(0)$ 的体积除以基本域 $\mathcal{F}$ 的体积。

这是合理的，因为 $\#(\mathbb{B}_R(0)\cap L)$ 应该近似于 $\mathbb{B}_R(0)$ 中能够容纳的 $\mathcal{F}$ 的数量。

例如，如果我们令 $L=\mathbb{Z}^2$，则这条原理告诉我们一个圆的面积约等于落在该圆内的整数点的个数。

![](https://pica.zhimg.com/v2-582ab3fecbd02d435c6ac0ec9257cffc_1440w.jpg)

图 1. 半径为 2 的圆(笔者所绘)


而关于误差项的估计：

$\#\{(x,y) \in \mathbb{Z}^2:\ x^2+y^2 \leq R^2\} = \pi R^2 +\text{(error term)}\\$

是一个著名的经典问题。随着维数的增大，问题会更加困难，因为当半径不够大时，由靠近球边界的格点所造成的误差会相当大。因此下面的估计：

$\#\{v \in L:\ \left\lVert v \right\rVert \leq R\}\approx \frac{\text{Vol}(\mathbb{B}_R(0))}{\text{Vol}(\mathcal{F})}\\$

在 $n$ 很大且 $R$ 不够大的情况下是有问题的。尽管如此，我们仍然可以寻找使右边等于1的 $R$ 的值，因为从某种意义上说，这个 $R$ 值是我们可能首次在球内发现非零格点的那个半径值。

考虑 $n$ 很大的情形，我们用球体体积的估计值公式计算。令：

$\sqrt{\frac{2\pi e}{n}}R \approx\text{Vol}(\mathbb{B}_R(0))^{1/n}\quad \text{equal to}\quad \text{Vol}(\mathcal{F})=\det(L),\\$

解得：

$R\approx \sqrt{\frac{n}{2\pi e}}(\det(L))^{1/n}.\\$

我们便推出了下面的启发式算法。

**Definition.** 设 $L$ 是 $n$ 维的 lattice。高斯的期望最短长度(Gaussian expected shortest length)是：

$\sigma(L) = \sqrt{\frac{n}{2\pi e}}(\det(L))^{1/n}.\\$

高斯的启发式(Gaussian heuristic)方法指的是：一个随机选择的格中，最短非零向量将满足：

$\left\lVert v_{\text{shortest}}\right\rVert \approx \sigma(L).\\$

更精确来说，若 $\epsilon > 0$ 固定，那么对于所有足够大的 $n$，一个随机选择的 $n$ 维格满足：

$(1-\epsilon) \sigma(L) \leq\left\lVert v_{\text{shortest}}\right\rVert\leq(1+\epsilon)\sigma(L).\\$

_Remark._ 对于较小的 $n$ 值，使用体积的精确公式更好，此时高斯的期望最短长度为：

$\sigma(L)=\frac{\Gamma(1+n/2)}{\sqrt{\pi}}(\det(L))^{1/n}\\$

我们会发现高斯启发式方法在量化格中 SVP 的困难程度时很有用。特别是，如果一个特定格 $L$ 的实际最短向量明显比 $\sigma(L)$​ 短，那么诸如 LLL 等格约化算法在定位最短向量时似乎就会容易得多。

_Example._ 设 $(m_1,\dots,m_n,S)$ 是一个背包问题。相关联的格 $L_{M,S}$ 是由 $(*)$ 矩阵的行生成的。矩阵 $L_{M,S}$ 的维度为 $n+1$，行列式为 $\det(L_{M,S})=2^nS$。在子集和问题一节中说过，$S$ 的大小满足 $S=O(2^{2n})$，所以 $S^{1/n}\approx 4$。所以我们可以估计高斯的最短长度为：

$\begin{align}\sigma(L_{M,S})&=\sqrt{\frac{n+1}{2\pi e}}(\det(L_{M,S}))^{1/(n+1)}=\sqrt{\frac{n+1}{2\pi e}}(2^nS)^{1/(n+1)}\\&\approx\sqrt{\frac{n}{2\pi e}}\cdot2S^{1/(n+1)}\approx\sqrt{\frac{n}{2\pi e}}\cdot8\approx 1.936\sqrt{n}.\\\end{align}\\$

这就证明了在子集和一节所说的，格 $L_{M,S}$ 包含一个长度为 $\sqrt{n}$ 的向量 $t$，并且知道 $t$ 就可以求得子集和问题的解。因此，解决格 $L_{M,S}$ 的 SVP 问题就很可能解决子集和问题。有关使用格中的方法解决子集和问题的进一步讨论，可以见专栏最后一篇文章的第二个例子。

我们会发现高斯启发式方法在量化寻找格中短向量的难度方面很有用。特别是，如果特定格 $L$ 的实际最短向量明显短于 $\sigma(L)$，那么像 LLL 这样的格约化算法在定位最短向量时似乎要容易得多。

将高斯启发式方法应用于 CVP 也有类似的结果。设 $L \subset \mathbb{R}^n$ 是一个 $n$ 维的 lattice，$w\in \mathbb{R}^n$ 是一个随机点，那么我们期望与 $w$ 最接近的格向量满足：

$\left\lVert v - w\right\rVert \approx\sigma(L).\\$

与 SVP 类似，如果 $L$ 包含一个与 $w$ 之间的距离比 $\sigma(L)$​ 小得多的向量，则格约化算法在解决 CVP 时就会更容易。

## Babai's algorithm and using a “good” basis to solve apprCVP

> 这一节对应教材的6.6.

如果格 $L \subset \mathbb{R}^n$ 有一组相互正交的基 $v_1,\dots,v_n$，即满足：

$v_i \cdot v_j = 0 \quad\text{for all }i\neq j,\\$

则我们可以轻松解决 SVP 和CVP。为解决 SVP，我们观察到 $L$ 中的任何向量的长度都由下面公式给出：

$\left\lVert a_1v_1+\dots+a_nv_n\right\rVert^2=a_1^2\left\lVert v_1 \right\rVert^2+\dots+a_n^2\left\lVert v_n \right\rVert^2.\\$

因为 $a_1,\dots,a_n\in \mathbb{Z}$，所以 $L$ 中的最短非零向量就是集合 $\{\pm v_1,\dots,\pm v_n\}$ 中的最短向量。即

$v_{\text{shortest}}=\{v_i:\ \left\lVert v_i \right\rVert=\min\{\left\lVert v_1 \right\rVert, \dots, \left\lVert v_n \right\rVert\} \}\\$

类似地可以解决 CVP。我们想要寻找 $L$ 中的一个最短向量，使其与给定向量 $w\in \mathbb{R}^n$ 的距离最近。我们首先将 $w$ 表示为：

$w=t_1v_1+\dots+t_nv_n \quad \text{with }t_1,\dots,t_n\in \mathbb{R}.\\$

那么对于 $v=a_1v_1+\dots+a_nv_n \in L$，我们有：

$\left\lVert v-w \right\rVert^2=(a_1-t_1)^2\left\lVert v_1 \right\rVert^2+\dots+(a_n-t_n)^2\left\lVert v_n \right\rVert^2.\\$

$a_i$ 是整数，因此上式要想取得最小值，我们只需将每个 $a_i$ 设置为与相应的 $t_i$ 最为接近的整数即可。

如果基中的向量是相互正交的，那么我们很有可能能够成功解决 CVP；但是如果基向量高度不正交，那么该算法就不会运行得很好。我们简要讨论一下潜在的几何原理，然后描述一般的方法，最后以一个二维的例子作结。

$L$ 的一组基确定了一个基本域 $\mathcal{F}$，我们在基本域一节已经证明了：用 $L$ 中的元素对 $\mathcal{F}$ 进行平移将会得到整个 $\mathbb{R}^n$ 空间，因此任何 $w\in \mathbb{R}^n$ 都有 $\mathcal{F}$ 的唯一一个平移 $\mathcal{F}+v,\ v\in L$。我们将平行六面体(parallelepiped) $L+v$ 中最靠近 $w$ 的顶点(vertex)作为我们对 CVP 的假设解。找到最近的顶点其实是很容易，因为：

$w=v+\epsilon_1v_1+\epsilon_2v_2+\dots+\epsilon_nv_n\quad \text{for some }0\leq \epsilon_1,\epsilon_2,\dots,\epsilon_n <1,\\$

则我们只需对 $\epsilon_i$ 进行如下替换：

$\epsilon_i = \left\{\begin{aligned}0,&\quad \text{if }\ \epsilon_i<\frac{1}{2}\\1,&\quad \text{if }\ \epsilon_i\geq\frac{1}{2}\\\end{aligned}\right.\\$

下图展示了整个过程：

![](https://pic4.zhimg.com/v2-8fefebe020c0e75599f816e4314c781b_1440w.jpg)

图 2. 尝试用给定的基本域来求解 CVP，源自《An Introduction to Mathematical Cryptography》


观察图 2，看上去这个过程一定有效，但这是因为图中的基向量彼此相对较为正交(reasonably orthogonal to one another)。图 3 说明了同一个格内的两组不同的基。第一个基是“好的(good)”，因为这些向量相当正交(fairly orthogonal)；第二个基是“坏的(bad)”，因为基向量之间的角度非常小。

![](https://pic3.zhimg.com/v2-e82abbf0951c90ba2324da2d86ce38d6_1440w.jpg)

图 3. 同一个格的两组不同的基，源自《An Introduction to Mathematical Cryptography》


如果我们尝试使用一个坏的基来求解 CVP，就像图 4 所示，我们可能会遇到问题。非格点的目标点实际上非常接近一个格点(见图 4 中的 Target Point 与 Closest Lattice Point)，但由于平行四边形过于细长，最靠近目标点的顶点实际上相当远(Target Point 与 Closest Vertex)。需要注意的是，随着格的维度增加，这些困难会变得更加严重。在二维或三维，甚至四维或五维中可视化的例子，并不能充分展示在基不够正交的情况下，最近顶点算法在解决 CVP 甚至是 apprCVP 上的失败程度。

![](https://pic4.zhimg.com/v2-c67ab4f68f3fa2286a3de21b22c6ef13_1440w.jpg)

图 4. 对于“坏的”基，Babai algorithm 的效果会很差。源自《An Introduction to Mathematical Cryptography》

  

**Theorem (Babai's Closest Vertex Algorithm).** 设 $L \subset \mathbb{R}^n$ 是一个 $n$ 维的 lattice，$v_1,\dots,v_n$ 是其一组基，令 $w$ 是 $\mathbb{R}^n$​ 中任意的一个向量。如果基底中的向量相互足够正交，那么我们有以下算法来解决 CVP。

![](https://pic3.zhimg.com/v2-aa570079f49ddf4578b220bd981e1206_1440w.jpg)

图 5. Babai algorithm。源自《An Introduction to Mathematical Cryptography》

> $\lfloor t_i\rceil$ 符号表示对 $t_i$ 四舍五入为整数。

一般来说，如果基中的向量彼此较为正交，那么该算法可以解决某种形式的 apprCVP。但是，如果基向量高度非正交，那么算法返回的向量通常与 $w$​ 相距甚远。

_Example._ 设 $L \subset \mathbb{R}^2$ 是一个 2 维的 lattice。我们给定一组基：

$v_1=(137,312) \quad \text{and}\quad v_2=(215,-187).\\$

我们将用 Babai's algorithm 来寻找 $L$ 的一个向量，使其与下面的向量最为接近：

$w=(53172, 81743).\\$

首先我们将 $w$ 表示为 $v_1,v_2$ 的实系数线性组合的形式。即我们需要寻找 $t_1, t_2 \in \mathbb{R}$ 满足：

$w = t_1 v_1+t_2v_2.\\$

我们可以得到两个线性方程：

$53172=137t_1+215t_2 \quad \text{and} \quad 81743=312t_1-187t_2.\\$

或者我们可以用矩阵的形式表示，

$(53172,81743)=(t_1,t_2)\left(\begin{array}1137 & 312\\215 &-187\\\end{array}\right).\\$

不管哪种方式，我们都能很轻易地计算 $(t_1,t_2)$。最后求出 $t_1\approx296.85,\ t_2\approx 58.15$。Babai's algorithm 告诉我们将 $t_1,\ t_2$ 圆整(round，即四舍五入)到最近的整数，然后计算：

$\begin{aligned}v&=\lfloor t_1\rceil v_1+\lfloor t_2\rceil v_2\\&=297\cdot(137,312)+58\cdot(215,-187)\\&=(53159,81818).\end{aligned}\\$

$v\in L$ 且 $v$ 应该接近于 $w$。我们发现：

$\left\lVert v-w \right\rVert \approx 76.12\\$

的确足够小。这是可以预测的，因为给定基中的向量彼此相当正交，这一点可以从 Hadamard 比率就可以看出：

$\mathcal{H}(v_1,v_2)=\left(\frac{\det(L)}{\left\lVert v_1\right\rVert \left\lVert v_2\right\rVert} \right)^{1/2}\approx \left(\frac{92699}{340.75 \times 284.95}\right)^{1/2}\approx 0.977\\$

非常接近于 1.

我们现在尝试用一组新的基来解决同样的问题：

$v_1^{'}=(1975,438)=5v_1+6v_2 \quad\text{and}\quad v_2^{'}=(7548,1627)=19v_1+23v_2.\\$

线性方程组

$(53172,81743)=(t_1,t_2)\left(\begin{array}11975 & 438\\7548 & 1627\\\end{array}\right)\\$

的解为 $(t_1,t_2)\approx (5722.66,-1490.34)$，于是我们令：

$v^{'}=5723v_1^{'}-1490v_2^{'}=(56405,82444).\\$

则 $v^{'}\in L$，但 $v^{'}$ 并没有足够接近 $w$，因为：

$\left\lVert v^{'}-w \right\rVert \approx 3308.12.\\$

基底 $\{v_1^{'},v_2^{'}\}$ 的非正交性也反映在 Hadamard 比率上：

$\mathcal{H}(v_1^{'},v_2^{'})=\left(\frac{\det(L)}{\left\lVert v_1^{'}\right\rVert \left\lVert v_2^{'}\right\rVert} \right)^{1/2}\approx \left(\frac{92699}{2022.99 \times 7721.36}\right)^{1/2}\approx 0.077\\$
