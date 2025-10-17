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
q\=ΔL⋅q0  
with q0≥Δ, which will dictate how many bits we want before the decimal part. Indeed, if we suppose we want 30 bits of precision for the decimal part, and 10 bits of precision for the integer part, we will set:  
设置为 q0≥Δ ，这将决定小数部分前需要多少位。例如，假设小数部分需要 30 位精度，整数部分需要 10 位精度，则需要设置：  
Δ\=230,q0\=2\\# bits integer⋅2\\# bits decimal\=210+30\=240

Once we have set the precision we want for the integer and decimal parts, chosen the number L of multiplications we want to perform, and set q accordingly, it is pretty easy to define the rescaling operation: we simply divide and round our ciphertext.  
一旦我们设置了整数和小数部分所需的精度，选择了要执行的乘法次数 L ，并相应地设置了 q ，定义重新缩放操作就非常容易了：我们只需对密文进行除法和四舍五入即可。

Indeed, suppose we are at a given level l, so the modulo is ql. We have a ciphertext c∈R2ql. Then we can define the rescaling operation from level l to l−1 as:  
事实上，假设我们处于给定的级别 l ，那么模数是 ql 。我们有密文 c∈R2ql 。然后，我们可以将从级别 l 到 l−1 的重新缩放操作定义为：

RSl→l−1(c)\=⌊ql−1ql⋅c⌉modql−1\=⌊Δ−1⋅c⌉modql−1

because ql\=Δl⋅q0.  
因为 ql\=Δl⋅q0 。

So by doing so, there are two things we manage to do:  
因此，通过这样做，我们可以做两件事：

- Once we decrypt the product of two ciphertexts c,c′, with underlying values Δ.z,Δ.z′, after applying rescaling we have Δ.z.z′. Therefore the scale remains constant throughout our computations as long as we rescale after each multiplication.  
  一旦我们解密了两个密文 c,c′ 的乘积，其底层值为 Δ.z,Δ.z′ ，经过重新缩放后，我们得到 Δ.z.z′ 。因此，只要我们在每次乘法后重新缩放，缩放比例在整个计算过程中就保持不变。
- The noise is reduced, because we divide both the underlying plaintext values, but also the noisy part of the decryption, which is of the form μ+e if you remember well. Therefore rescaling also serves the purpose of noise reduction.  
  噪声降低了，因为我们不仅对底层明文值进行了除法运算，还对解密结果中的噪声部分进行了除法运算，如果你没记错的话，噪声部分的形式是 μ+e 。因此，重新缩放也起到了降低噪声的作用。

So if we put everything together, to actually do a multiplication in CKKS you need to do three things:  
因此，如果我们把所有东西放在一起，要在 CKKS 中实际进行乘法，您需要做三件事：

1.  Compute the product: cmult\=CMult(c,c′)\=(d0,d1,d2)  
    计算乘积： cmult\=CMult(c,c′)\=(d0,d1,d2)
2.  Relinearize it: crelin\=Relin((d0,d1,d2),evk)  重新线性化： crelin\=Relin((d0,d1,d2),evk)
3.  Rescale it: crs\=RSl→l−1(c)  重新缩放： crs\=RSl→l−1(c)

Once you do all this, decryption with the secret key will provide the right result and we are all set! Well, almost there, as there is one last detail we will have to cover.  
完成所有这些操作后，使用密钥解密将提供正确的结果，一切就绪！好了，差不多了，还有最后一个细节需要讲解。

## Chinese remainder theorem

中国剩余定理

So we saw we had everything we needed, but there is one technical problem: computations are done on huge numbers! Indeed we have that operations are done with huge moduli ql\=Δl.q0. Imagine for instance we want 30 bits of precision for the decimal part, 10 for the integer part, and 10 multiplications. Then we have qL\=Δl.q0\=230×10+40\=2340!  
看来我们已经拥有了所需的一切，但还有一个技术问题：计算是在巨大的数字上进行的！事实上，这些运算是用巨大的模数 ql\=Δl.q0 进行的。想象一下，例如，我们希望小数部分精度为 30 位，整数部分精度为 10 位，并进行 10 次乘法运算。那么我们就得到了 qL\=Δl.q0\=230×10+40\=2340 ！

Because we handle sometimes huge polynomials, such as the uniformly sampled ones, some computations won’t fit in usual 64 bits systems so we have to find a way to make it work.  
因为我们有时会处理巨大的多项式，例如均匀采样的多项式，所以某些计算不适合通常的 64 位系统，所以我们必须找到一种方法来使其发挥作用。

That’s where the [Chinese remainder theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem) comes in! This theorem states that if we have L coprime numbers p1,…,pL, p\=∏Ll\=1pl their product, then the map  
这就是中国剩余定理的用武之地！该定理指出，如果我们有 L 个互质数， p1,…,pL ， p\=∏Ll\=1pl 个它们的乘积，那么映射  
Z/pZ→Z/p1Z×⋯×Z/pLZ:x ( mod p)↦(x ( mod p1),…,x ( mod pL))  
is a ring isomorphism, i.e. if you want to perform arithmetic on the “big” ring Z/pZ, you could instead perform it independently on the “small” rings Z/plZ where you will not have the problem of performing computation on more than 64 bits.  
是环同构，即如果您想在“大”环 Z/pZ 上执行算术运算，那么您可以在“小”环 Z/plZ 上独立执行该运算，这样就不会遇到在超过 64 位上执行计算的问题。

So in practice, instead of having qL\=ΔL.q0, we first choose p1,…,pL,q0 prime numbers, with each pl≈Δ and q0 a prime number greater than Δ depending on the integer precision desired, then set qL\=∏Ll\=1pl⋅q0.  
因此在实践中，我们首先选择 p1,…,pL,q0 个素数，而不是 qL\=ΔL.q0 ，其中 pl≈Δ 和 q0 均为大于 Δ 的素数，具体取决于所需的整数精度，然后设置 qL\=∏Ll\=1pl⋅q0 。

This way, we can use the Chinese remainder theorem, and do the little trick described above to be able to perform arithmetic with big modulo. The rescaling operation has to be slightly modified:  
这样，我们就可以利用中国剩余定理，并运用上面提到的小技巧，进行大模运算。缩放操作需要稍微修改一下：  
RSl→l−1(c)\=⌊ql−1qlc⌉ (mod ql−1)\=⌊p−1lc⌉ (mod ql−1)

So we have seen in this article what is rescaling, why we need it, and how one could implement it in practice. In the next and last article we will put everything together and code a CKKS-like homomorphic encryption scheme ourselves in Python!  
我们已经在本文中了解了什么是重新缩放，为什么需要它，以及如何在实践中实现它。在下一篇也是最后一篇文章中，我们将把所有内容整合在一起，并用 Python 编写一个类似 CKKS 的同态加密方案！

