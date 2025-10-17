

## CKKS explained series  CKKS 系列解说

[Part 1, Vanilla Encoding and Decoding  
第 1 部分，Vanilla 编码和解码](https://blog.openmined.org/ckks-explained-part-1-simple-encoding-and-decoding/)  
[Part 2, Full Encoding and Decoding  
第 2 部分，全编码和解码](https://blog.openmined.org/ckks-explained-part-2-ckks-encoding-and-decoding/)  
[Part 3, Encryption and Decryption  
第 3 部分，加密和解密](https://blog.openmined.org/ckks-explained-part-3-encryption-and-decryption/)  
Part 4, Multiplication and Relinearization  
第 4 部分，乘法和重新化  
[Part 5, Rescaling  第 5 部分，重新缩放](https://blog.openmined.org/ckks-explained-part-5-rescaling/)

## Introduction  介绍

在上一篇文章[《CKKS 详解，第三部分：加密与解密》](https://blog.openmined.org/ckks-explained-part-3-encryption-and-decryption)中，我们了解了如何基于环学习误差（RLWE）问题创建一个同态加密方案，并实现了同态加法以及密文 - 明文乘法。

**虽然密文与明文的乘法运算很容易执行，但我们将会看到，密文与密文的乘法运算要复杂得多**。实际上，要正确进行这种运算，我们需要处理很多事情，比如找到合适的运算方式，以确保解密后能得到两个密文的乘积，以及管理密文的大小。

因此，本文将介绍密文 - 密文乘法和重线性化的概念，以减小所得密文的大小。

## Recap of basic operations

为了了解我们将如何在CKKS中执行密文-密文乘法，让我们回顾一下在上一篇文章中看到的内容。

首先，请记住我们研究的是多项式空间$\mathcal{R}_q=\mathbb{Z}_q[X]/(X^N+1)$。我们选取 $s$ 作为私钥，然后就可以安全地输出公钥 $p=(b,a)=(-a·s+e,a)$，其中 $a$ 是从 $\mathcal{R}_q$ 中均匀采样得到的，$e$ 是一个小的随机多项式。

然后我们有 $\mathrm{Encrypt}(\mu,p)=c=(c_0,c_1)=(\mu,0)+p=(b+\mu,a)\in\mathcal{R}_q^2$，这是使用公钥 $p$ 对明文$\mu\in\mathbb{Z}_q[X]/(X^N+1)$进行的加密操作。  

>$b=-a·s+e$
>
>$\mu-b=\mu-a·s+e=c_0$

要使用密钥解密密文 $c$，我们执行以下操作：：  
$$
\mathrm{Decrypt}(c,s)=c_0+c_1\cdot s=\mu–a\cdot s+e+a\cdot s=\mu+e\approx\mu.
$$
然后我们发现，在密文上定义一个加法运算$\mathrm{CAdd}(c,c^{\prime})$是很容易的，这样一来，一旦我们对$\mathrm{CAdd}$的输出进行解密，就能近似得到两个基础明文的和。  
执行此作的方法是定义 $\mathrm{CAdd}$ 如下：  
$$
\mathtt{CAdd}(c,c^{\prime})=(c_0+c_0^{\prime},c_1+c_1^{\prime})=c+c^{\prime}=c_{add}
$$
事实上，如果我们对其执行解密操作，我们会得到： 
$$
\mathrm{Decrypt}(c_{add},s)=c_0+c_0^\prime+(c_1+c_1^\prime)\cdot s=c_0+c_1\cdot s+c_0^\prime+c_1^\prime\cdot  s=\mathrm{Decrypt}(c,s)+\mathrm{Decrypt}(c^{\prime},s)\approx\mu+\mu^{\prime}
$$
在这里我们可以看到，对密文进行加法运算相当简单直接，我们只需要将两个密文相加，然后就可以使用常规的解密操作对结果进行解密，从而得到两个底层明文相加的结果。
我们将看到，在进行密文-密文乘法时，乘法和解密作都更加复杂。

## Ciphertext-ciphertext multiplication

那么既然我们已经了解了这一点，就会明白我们的目标是找到运算$\mathtt{CMult,DecryptMult}$，使得对于两个密文 $c$、$c^\prime$，我们有：

$$
\text{DecryptMult}(\mathsf{CMult}(c,c^{\prime}),s)=\mathsf{Decrypt}(c,s)\cdot\mathsf{Decrypt}(c^{\prime},s).
$$


记住这一点 $\mathsf{Decrypt}(c,s)=c_0+c_1\cdot s$ 。因此，如果我们开发上面的表达式，我们会得到：
$$
\mathtt{Decrypt}(c,s)\cdot\mathtt{Decrypt}(c^{\prime},s)=(c_0+c_1s)\cdot(c_0{}^{\prime}+c_1{}^{\prime}s)=c_0c_0{}^{\prime}+(c_0c_1{}^{\prime}+c_0{}^{\prime}c_1)s+c_1c_1{}^{\prime}s^2=d_0+d_1s+d_2s^2\\with \\

d_0=c_0c_0^{\prime},d_1=(c_0c_1^{\prime}+c_0^{\prime}c_1),d_2=c_1c_1^{\prime}
$$
有意思！仔细想想，对$\mathrm{Decrypt}(c,s)=c_0+c_1s$的评估可以看作是对密钥 $s$ 的多项式评估，而且它是一个一次多项式，形式为$c_0+c_1S$，其中 $S$ 是多项式变量。

因此，如果我们观察对两个密文乘积的解密操作，会发现它可以看作是在密钥 $s$ 上对二次多项式$d_0+d_1S+d_2S^2$进行求值。

因此，我们可以看出，我们可以使用以下运算来进行密文 - 密文乘法：

+ $\mathsf{CMult}(c,c^{\prime})=c_{mult}=(d_0,d_1,d_2)=(c_0c_0^{\prime},c_0c_1^{\prime}+c_0^{\prime}c_1,c_1c_1^{\prime})$
+ $\text{DecryptMult}(c_{mult},s)=d_0+d_1s+d_2s^2$

使用此类操作可能会奏效，但存在一个问题：密文的大小增加了！实际上，通常密文只包含几个多项式，而在这里，我们的密文有 $3$ 个多项式。按照之前的思路，如果我们不采取任何措施，要正确解密下一个乘积，就需要 $5$ 个多项式，之后是 $9$ 个，依此类推。因此，密文的大小会呈指数级增长，如果我们像这样定义密文与密文的乘法，在实际应用中就无法使用了。
我们需要找到一种方法来进行乘法，而不增加每一步的密文大小。这就是重新化的用武之地！

## Relinearization  

因此，我们了解到可以将密文之间的乘法定义为运算$\mathbf{CMult}(c,c^{\prime})=(d_0,d_1,d_2)$。问题在于，现在输出的是一个维度为 $3$ 的密文，而且如果在每次计算后密文的规模持续增大，那么在实际应用中就会变得难以操作。

那么我们来思考一下，问题是什么呢？问题在于我们需要第三个项，也就是 $d_2$ 项，它用于多项式解密$\text{DecryptMult}(c_{mult},s)=d_0+d_1.s+d_2.s^2$。但是，如果我们能以某种方式找到一种方法，只用一个一次多项式来计算 $d_2·s²$，就像常规解密那样，会怎么样呢？那样的话，密文的大小就会是恒定的，它们都只会是几个多项式而已！

这正是再线性化的核心：找到一对多项式$(d_0’,d_1’)=\mathrm{Relin}(c_{mult})$，使得：

>$c_{mult}=(d_0,d_1,d_2)=(c_0c_0^{\prime},c_0c_1^{\prime}+c_0^{\prime}c_1,c_1c_1^{\prime})$

$$
\mathtt{Decxypt}((d_0^{\prime},d_1^{\prime}),s)=d_0^{\prime}+d_1^{\prime}.s=d_0+d_1.s+d_2.s^2=\mathtt{Decrypt}(c,s)\cdot\mathtt{Decrypt}(c^{\prime},s)
$$

即重新线性化允许存在一个多项式对（而非三元组），**这样一来，当使用仅需秘密密钥（而非其平方）的常规解密电路对其进行解密时，我们就能得到两个基础明文的乘积。**

因此，如果我们在每次密文与密文相乘后都进行重线性化，那么我们将始终得到相同大小的密文，并且解密电路也相同！

现在你可能想知道，我们实际上需要如何定义$\mathrm{Relin}$才能得到这样的结果。思路很简单，我们知道需要有几个多项式，使得$d_0^{\prime}+d_1^{\prime}.s=d_0+d_1.s+d_2.s^2$。我们的想法是，将$(d_0^{\prime},d_1^{\prime})=(d_0,d_1)+P$，其中 $P$ 代表一组多项式，满足解密$\mathrm{Decrypt}(P,s)=d_2.s^2$。

这样一来，当我们在$(d_0’,d_1’)$上评估解密电路时，我们会得到：
$$
\mathtt{Decrypt}((d_0’,d_1’),s)=\mathtt{Decrypt}((d_0,d_1),s)+\mathtt{Decrypt}(P,s)=d_0+d_1.s+d_2.s^2
$$
一种实现方法是提供一个评估密钥，它将用于计算 $P$ 。令 $\mathrm{evk}=\begin{pmatrix}-a_0.s+e_0+s^2,a_0\end{pmatrix}$，其中 $e_0$ 是一个小的随机多项式，$a_0$ 是在 $\mathcal{R}_q$上均匀采样的多项式。那么，如果我们应用$\mathrm{Decrypt}(\mathrm{evk},s)=e_0+s^2\approx s^2$。这很好！我们可以看到，我们可以向执行计算的一方公开分享评估密钥，因为基于RLWE问题，很难提取出秘密，而且该密钥可用于求解平方项。

那么，$P$（即应该解密为$d_2.s^2$的密文）的一个可能候选值可以简单地是$P=d_2.\mathrm{~evk}=\begin{pmatrix}d_2.(-a_0\cdot s+e_0+s^2),d_2.a_0\end{pmatrix}$。实际上，正如我们所看到的，我们有$\mathbf{Decrypt}(P,s)=d_2.s^2+d_2.e_0$。那么，我们能否像往常一样，认为$d_2.s^2+d_2.e_0\approx d_2.s^2$呢？

不幸的是，我们无法那样做，因为$d_2.e_0$项比我们通常遇到的噪声大得多。正如你之前所注意到的，我们之所以允许对结果进行近似处理，是因为误差多项式很小，例如，它是一些小多项式的和，不会对结果产生太大影响。但这里的问题在于，$d_2$ 会很大，因为$d_2=c_1c_1^{\prime}$，而每个 $c_1$ 都包含一个在 $\mathcal{R}_q $ 上均匀采样的多项式 $a$ ，因此，它比我们通常处理的那些小误差多项式大得多。

那么在实际中我们该如何处理这个问题呢？关键在于对评估密钥稍作修改，将其定义为$\mathrm{evk}=\begin{pmatrix}-a_0.s+e_0+p.s^2,a_0\end{pmatrix}\mathrm{~mod~}p.q$，其中 $p$ 是一个大整数，$a_0$ 是从 $\mathcal{R}_{p·q}$中均匀采样得到的。这里的思路是，我们会除以 $p$ 来减少由与 $d_2$ 相乘所引入的噪声，因此最终我们会得到：  
$$
P=\begin{bmatrix}p^{-1}\cdot d_2\cdot\mathrm{evk}\end{bmatrix}\mathrm{~mod~}q\\=p^{-1}\cdot (d_2.(-a_0\cdot s+e_0+p\cdot s^2),d_2\cdot a_0)\\
$$
这意味着我们要除以 $p$ 并将结果四舍五入到最接近的整数，然后对 $q$取模（而不是对 $p·q$ 取模）

好了，我们终于有了自己的候选方案！那么，要定义重线性化，我们需要一个评估密钥（该密钥可以公开，没有风险），我们将其定义为：
$$
\mathrm{Relin}((d_0,d_1,d_2),\mathrm{evk})=(d_0,d_1)+\lfloor p^{-1}\cdot d_2\cdot\mathrm{evk}\rceil
$$
那么，如果我们有两个密文 $c、c^\prime$，并且我们想要将它们相乘（可能要乘好几次），然后对结果进行解密，其工作流程如下：

1.  将它们相乘：$c_{mult}=\mathrm{CMult}(c,c^{\prime})=(d_0,d_1,d_2)$
2.  重新线性化: $c_{relin}=\mathrm{Relin}((d_0,d_1,d_2),\mathrm{evk})$
3.  解密输出: $\mu_{mult}=\mathrm{Decrypt}(c_{relin},s)\approx\mu\cdot\mu^{\prime}$

