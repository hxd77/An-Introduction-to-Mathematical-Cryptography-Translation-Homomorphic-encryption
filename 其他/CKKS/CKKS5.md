## CKKS explained series  CKKS 讲解系列

[Part 1, Vanilla Encoding and Decoding  
第一部分，原始编码和解码](https://blog.openmined.org/ckks-explained-part-1-simple-encoding-and-decoding/)  
[Part 2, Full Encoding and Decoding  
第 2 部分，完整编码和解码](https://blog.openmined.org/ckks-explained-part-2-ckks-encoding-and-decoding/)  
[Part 3, Encryption and Decryption  
第 3 部分，加密和解密](https://blog.openmined.org/ckks-explained-part-3-encryption-and-decryption/)  
[Part 4, Multiplication and Relinearization  
第 4 部分，乘法和重线性化](https://blog.openmined.org/ckks-explained-part-4-multiplication-and-relinearization/)  
Part 5, Rescaling  第 5 部分，重新缩放

## Introduction  介绍

在CKKS解释的上一篇文章[《第4部分：乘法与重线性化》](https://blog.openmined.org/ckks-explained-part-4-multiplication-and-relinearization)中，我们了解了密文乘法在CKKS中是如何工作的，为什么我们需要对输出进行重线性化以保持恒定的密文大小，以及如何进行重线性化。

尽管如此，我们将会看到，我们需要一种名为重新缩放的最终操作来处理噪声并避免溢出。这将是本系列的最后一篇理论文章，而在下一篇也是最后一篇文章中，我们将用Python实现所有内容！

为了理解这是如何运作的，我们首先会有一个宏观的认识，然后再详细了解它的工作原理。

## High level view of the modulus chain

到目前为止，我们已经深入研究了CKKS的诸多细节，但接下来我们会退一步进行探讨。CKKS的运行涉及到我们所说的“层级”，其含义是，在噪声大到无法正确解密输出之前，允许进行的乘法运算次数是有限的。

你可以把这想象成一个油箱。起初，油箱里装满了汽油，但随着你执行越来越多的操作，油箱会被耗尽，直到汽油耗尽，你就再也做不了任何事了。分级同态加密方案也是如此：你一开始有一定量的“汽油”，但随着你进行乘法运算，“汽油”会越来越少，直到耗尽，这时你就再也无法执行任何操作了。

下图说明了这一点。开始时，你的油箱是满的。但当你进行乘法运算和重新缩放时，你会降低等级，这相当于消耗了一些汽油。因此，如果你从 $L$ 个等级开始，记为$(q_L,q_{L-1},\ldots,q_1)$，处于等级 $q_l$ 意味着你还剩下 $l$ 次乘法运算，而执行一次乘法运算会将等级从 $q_{l}$ 降至$q_{l-1}$。

![](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/rescaling.png)

Rescaling explained  重新缩放解释

就像在现实生活中一样，一旦你的汽油耗尽，你可以给油箱加油，以便能沿着道路行驶得更远。这种操作被称为“自举”，我们在本文中不会涉及这部分内容。所以，如果我们假设无法给油箱加油，那么在使用分级同态加密方案时，有一个有趣的方面是必须考虑的：你需要提前知道你将要进行的乘法运算的次数！

的确，就像在现实生活中一样，如果你计划去很远的地方旅行，你需要的汽油会比只是在小区周边转悠要多。这里的情况也是如此，根据你需要执行的乘法运算次数，你必须调整“油箱”的大小。但油箱越大，计算量就越繁重，而且你的参数安全性也会越低。的确，就像在现实生活中一样，如果你需要一个更大的油箱，它就会更重，这会让事情变慢，同时也会降低其安全性。

我们不会深入所有细节，但要知道CKKS方案的安全性基于 $\frac{N}q$比率，其中 $N$ 是我们多项式的次数，即向量的大小，而 $q$ 是系数模数，即我们的“油箱”。

因此，我们需要进行的乘法运算越多，“油箱”就越大，因此我们的参数安全性就会降低。为了维持相同的安全级别，我们就需要增大 $N$ ，而这会增加我们运算的计算成本。

下图来自微软私人人工智能训练营，展示了使用CKKS时必须考虑的这种权衡。为了保证128位的安全性，我们必须提高多项式的阶数，即使我们并不需要它提供的额外插槽，因为增大的模数可能会使我们的参数不安全。

![](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/security_params.png)

Security as a function of polynomial degree and modulo  
安全性是多项式度和模的函数

那么在我们进入更具理论性的部分之前，让我们来看看主要的收获是什么：

- 重新调整规模和噪声管理可以被看作是管理一个油箱：你从初始预算开始，使用得越多，预算就会越少。如果油用完了，你就再也做不了任何事情了。
- 你需要提前知道将要进行多少次乘法运算，这会决定“油箱”的大小，而“油箱”的大小又会影响你将使用的多项式的次数。

## Context  语境

既然我们现在已经了解了大致情况，那就让我们深入探究这一切的原因和运作方式吧。

如果你对第二部分关于编码的内容记得没错的话，若我们有一个初始值向量 $z$ ，在编码过程中会将其乘以一个缩放因子 $Δ$ ，以保持一定程度的精度。

因此，明文 $μ$ 和密文 $c$ 中包含的基础值是 $Δ⋅z$ 。问题在于，当我们将两个密文 $c$ 和 $c^\prime$ 相乘时，结果的值为 $z⋅z^\prime⋅Δ²$。这其中包含了缩放因子的平方，由于缩放因子可能会呈指数级增长，经过几次乘法运算后可能会导致溢出。此外，正如我们之前所看到的，每次乘法运算后，噪声都会增加。

因此，重缩放操作的目标实际上是保持规模恒定，同时减少密文中存在的噪声。

## Vanilla solution  香草溶液

那么我们该如何解决这个问题呢？要解决这个问题，我们需要了解如何定义 $q$。 请记住，这个参数 $q$ 被用作我们多项式环$\mathcal{R}_q=\mathbb{Z}_q[X]/(X^N+1)$中系数的模。

正如在概览中所描述的，$q$ 将被用作一个油箱，我们会在操作过程中逐渐将其排空。

如果我们假设必须进行 $L$ 次乘法运算，且其规模为 $Δ$ ，那么我们将把 $q$ 定义为： 
$$
q=\Delta^L\cdot q_0
$$

其中 $q_0≥Δ$，这将决定我们希望在小数部分之前有多少位。实际上，如果我们假设希望小数部分有 $30$ 位精度，整数部分有 $10$ 位精度，我们会设置：
$$
\Delta=2^{30},\quad q_0=2^{\backslash\#\text{ bits integer}}\cdot2^{\backslash\#\text{ bits decimal}}=2^{10+30}=2^{40}
$$


一旦我们设定好了对整数部分和小数部分所需的精度，选择了我们要执行的乘法运算次数 $L$，并相应地设定了 $q$，定义重缩放操作就变得相当简单了：我们只需对密文进行除法并取整即可。

的确，假设我们处于给定的层级 $l$，因此模数为 $q_l$。我们有一个密文$c\in\mathcal{R}_{q_l}^2.$。那么我们可以将从层级 $l$ 到 $l−1$ 的重缩放操作定义为：
$$
RS_{l\to l-1}(c)=\left\lfloor\frac{q_{l-1}}{q_l}\cdot c\right\rceil\quad\mathrm{mod}q_{l-1}=\left\lfloor\Delta^{-1}\cdot c\right\rceil\quad\mathrm{mod}q_{l-1}
$$
因为$q=\Delta^L\cdot q_0$  
因此，通过这样做，我们可以做两件事：

- 一旦我们解密两个密文 $c、c^\prime$的乘积（其对应的基础值为 $Δ.z$、 $Δ.z′$），在应用重缩放后，我们会得到 $Δ.z.z^\prime$。因此，只要在每次乘法后进行重缩放，计算过程中的规模就会保持不变。

- 噪声会减少，因为我们既对基础明文值进行了除法运算，也对解密过程中的噪声部分进行了除法运算，如果你记性好的话，噪声部分的形式是 $μ + e$。因此，重新缩放也起到了降噪的作用。

因此，如果我们把所有东西放在一起，要在 CKKS 中实际进行乘法，您需要做三件事：

1.  计算乘积： $c_{mult}=\mathrm{СМult}(c,c^{\prime})=(d_0,d_1,d_2)$
2.  重新线性化：$c_{relin}=\mathrm{Relin}((d_0,d_1,d_2),evk)$
3.  重新缩放： $c_{rs}=\mathrm{RS}_{l\to l-1}(c)$
    完成所有这些操作后，使用密钥解密将提供正确的结果，一切就绪！好了，差不多了，还有最后一个细节需要讲解。

## Chinese remainder theorem

所以我们发现我们拥有了所需的一切，但存在一个技术问题：计算是在极大的数字上进行的！实际上，我们的运算都是在极大的模数$q_l=\Delta^l.q_0$下完成的。例如，假设我们希望小数部分有 $30$ 位精度，整数部分有 $10$ 位精度，还要进行 $10$ 次乘法运算。那么我们就会得到$q_L=\Delta^l.q_0=2^{30\times10+40}=2^{340}!$

因为我们有时要处理庞大的多项式，比如那些均匀采样得到的多项式，一些计算在常规的 $64$ 位系统中无法进行，所以我们必须找到一种方法来使其可行。

这就是中国剩余定理的用武之地！该定理指出，如果我们有 $L$ 个互质的数$p_1,\ldots,p_L$，$p=\prod_{l=1}^Lp_l$，那么这个映射
$$
\mathbb{Z}/p\mathbb{Z}\to\mathbb{Z}/p_1\mathbb{Z}\times\cdots\times\mathbb{Z}/p_L\mathbb{Z}:x\left(\mathrm{~mod~}p\right)\mapsto\left(x\left(\mathrm{~mod~}p_1\right),\ldots,x\left(\mathrm{~mod~}p_L\right)\right)
$$


是一个环同构，也就是说，如果你想在“大”环$\mathbb{Z}/p\mathbb{Z}$上进行算术运算，你可以转而在“小”环$\mathbb{Z}/p_l\mathbb{Z}$上独立地进行运算，在这些小环上你不会遇到需要在超过 $64$ 位上进行计算的问题。

因此，在实际操作中，我们并非令$q_l=\Delta^l.q_0$，而是首先选择$p_1,\ldots,p_L$，$q_0$这些质数，其中每个 $p_l≈Δ$，而 $q_0$ 是一个大于 $Δ$ 的质数，其大小取决于所需的整数精度，然后令$q_L=\prod_{l=1}^Lp_l\cdot q_0$。

这样一来，我们就可以运用中国剩余定理，并采用上述的小技巧来进行大模运算。不过，重新缩放操作需要稍作修改：  
$$
RS_{l\to l-1}(c)=\left\lfloor\frac{q_{l-1}}{q_l}c\right\rceil({\mathrm{mod}}q_{l-1})=\left\lfloor p_l^{-1}c\right\rceil({\mathrm{mod}}q_{l-1})
$$


