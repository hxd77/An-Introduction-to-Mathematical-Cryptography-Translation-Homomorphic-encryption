## CKKS 系列

Part 1, 香草编码与解码  
[Part 2, Full Encoding and Decoding](https://blog.openmined.org/ckks-explained-part-2-ckks-encoding-and-decoding/)  
[Part 3, Encryption and Decryption](https://blog.openmined.org/ckks-explained-part-3-encryption-and-decryption/)  
[Part 4, Multiplication and Relinearization](https://blog.openmined.org/ckks-explained-part-4-multiplication-and-relinearization/)  
[Part 5, Rescaling](https://blog.openmined.org/ckks-explained-part-5-rescaling/)

## Introduction

同态加密是一个很有前途的领域，它允许对加密数据进行计算。这篇优秀的文章，什么是同态加密，广泛解释了什么是同态加密以及该研究领域的利害关系。

在本系列文章中，我们将深入研究 Cheon-Kim-Kim-Song （CKKS） 方案，该方案在论文 Homomorphic Encryption for Arithmetic of Approximate Numbers 中首次讨论。CKKS 允许我们对复值的向量（因此也是实值）执行计算。这个想法是，我们将在 Python 中从头开始实现 CKKS，然后，通过使用这些加密原语，我们可以探索如何执行复杂的作，例如线性回归、神经网络等。

关于CKKS的[视频资源](https://www.youtube.com/watch?v=iQlgeL64vfo)

![image-20251006213852098](https://raw.githubusercontent.com/hxd77/BlogImage/master/TyporaImage/20251006213852145.png)

图一、CKKS的高级视图

上图提供了 CKKS 的高级视图。我们可以看到，消息 $m$（我们要对其执行某些计算的值向量）首先被编码为明文多项式 $p（X）$，然后使用公钥进行加密。

CKKS 使用多项式，因为与向量上的标准计算相比，它们在安全性和效率之间提供了良好的权衡。

一旦消息 $m$ 被加密为 $c$（几个多项式），CKKS 就会提供可以对其执行的多种运算，例如加法、乘法和旋转

如果我们用 $f$ 表示一个函数，它是同态运算的组成，那么使用密钥解密 $c^{\prime} = f（c）$ 将产生 $p' = f（p）$。因此，一旦我们解码它，我们将得到 $m = f（m）$。

实现同态加密方案的中心思想是在编码器、解码器、加密器和解密器上具有同态属性。这样，密文作将被正确解密和解码，并提供输出，就像直接对明文进行作一样。

所以在本文中我们将了解如何实现编码器和解码器，在后面的文章中我们将继续实现加密器和解密器以具有同态加密方案。



**Preliminaries**

建议具备线性代数和环理论的基础知识，以便对 CKKS 的实施方式有很好的理解。您可以使用以下链接熟悉这些主题：

- [Introduction to linear algebra](https://math.mit.edu/~gs/linearalgebra/) provides a good basis in linear algebra.
- [Ring theory (Math 113)](https://math.berkeley.edu/~mcivor/math113su16/113ringnotes2016.pdf) is a good resource to learn ring theory.

具体到本文，我们将依赖以下概念：

- [分圆多项式](https://en.wikipedia.org/wiki/Cyclotomic_polynomial)是具有良好属性的多项式，因为它们在用作多项式模时允许高效计算。

>### 1 分圆多项式的理解
>
>互素或互质 `(Coprime Integers)` : 若整数 $a$ 与整数 $b$ 的唯一公约数为 $1$ ，则称 $a$ 与 $b$ 互素或互质 `(coprime integers)` 。因此，任何能被 $a$ 整除的质数都不能被 $b$ 整除，反之亦然。也即两者的最大公约数 `(Greatest Common Divisor, GCD)` 为 $1$ 。
>
>
>简单描述：分圆多项式可以简单理解为多项式 $x^n - 1$ 分解后，所得的不可约多项式。
>
>
>
>正式定义为：在数论中，对于任意正整数 $n$ ， $n$ 次分圆多项式 `(nth cyclotomic polynomial)` 是一个具有整数系数的唯一不可约多项式 $\phi_n(x)$ `(the unique irreducible polynomial with integer coefficients)` 。其中，对于任何 $k < n$ , $\phi_n(x)$ 是 $x^n-1$ 的一个因子，但不是 $x^k-1$ 的一个因子。**该分圆多项式的根为n次原语单元根 `(nth primitive roots of unity)` $e^{2i\pi \frac{k}{n}}
>$** ，**其中， $k$ 为不大于 $n$ 的正整数，且 $k$ 与 $n$ 为互质数。**换句话说， $n$ 次分圆多项式 `(nth cyclotomic polynomial)` 为：
>$$
>\phi_n(x) = \displaystyle\prod_{1≤k≤n \atop gcd(k,n)=1}(x - e^{2i\pi \frac{k}{n}})
>$$
>
>
>### 2 举例说明计算方式
>
>> 因计算过程中，常使用到 $cos/sin$ 的计算，结合下图可快速得出它们的结果。
>
>![img](https://raw.githubusercontent.com/hxd77/BlogImage/master/TyporaImage/20251008165940776.jpeg)
>
>> 复数计算1：由于 $e^{i\theta} = cos(\theta) + i \cdot sin(\theta)$ ，可得 $e^{2i\pi \frac{k}{n}}=cos(2\pi \frac{k}{n}) + i \cdot sin(2\pi \frac{k}{n})
>> $ 
>> 复数计算2： $i^2=-1$ 
>
>#### 2.1 演算 $\phi_1(x) = x - 1$
>
>- 仅存在一种情况： $n=1, k=1$ 
> 因 $cos(2\pi) + i \cdot sin(2\pi) = 1$ ，所以 $\phi_1(x) = x - 1$
>
>#### 2.2 演算 $\phi_2(x) = x + 1$
>
>+ 仅存在一种情况： $n=2, k=1$ 
> 因 $cos(\pi) + i \cdot sin(\pi) = -1$ ，所以 $\phi_2(x) = x + 1$
>
>#### 2.3 演算 $\phi_3(x) = x^2 + x + 1$
>
>+ 情况 $1$ ： $n=3, k=1$ 
> 因 $cos(\frac{2\pi}{3}) + i \cdot sin(\frac{2\pi}{3}) = -\frac{1}{2} + \frac{\sqrt{3}}{2} \cdot i
>  $
>
>+ 情况 $2$ ： $n=3, k=2$ 
> 因 $cos(\frac{4\pi}{3}) + i \cdot sin(\frac{4\pi}{3}) = -\frac{1}{2} - \frac{\sqrt{3}}{2} \cdot i
>  $
>
>所以 $\phi_3(x) = (x + \frac{1}{2} - \frac{\sqrt{3}}{2} \cdot i) \cdot (x + \frac{1}{2} + \frac{\sqrt{3}}{2} \cdot i) ={(x + \frac{1}{2})^2} -{(\frac{\sqrt{3}}{2} \cdot i)^2} =x^2 + x +\frac{1}{4} -{(-\frac{3}{4})}=x^2 + x + 1
>$ 
>
>#### 2.4 演算 $\phi_4(x) = x^2 + 1$
>
>+ 情况 $1$ ： $n=4, k=1$ 
> 因 $cos(\frac{\pi}{2}) + i \cdot sin(\frac{\pi}{2}) = i
>  $
>
>+ 情况 $2$ ： $n=4, k=3$ 
> 因 $cos(\frac{3\pi}{2}) + i \cdot sin(\frac{3\pi}{2}) = -i
>  $
>
>所以 $\phi_4(x) = (x - i) \cdot (x + i) =x^2 -{(-1)}=x^2 + 1$ 
>
>同理，可得 $\phi_5(x),\phi_6(x)...$ 
>
>综述，从 $1$ 到 $30$ 的分圆多项式为：
>
>![](https://raw.githubusercontent.com/hxd77/BlogImage/master/TyporaImage/20251008170617940.png)
>
>### 3 有趣的性质
>
>#### 3.1 同态加密常用的一个性质
>
>$$
>\phi_{2^{h}}(x) = x^{{2}^{(h-1)}} + 1
>$$
>
>因此，若 $N= 2^k$ ，则 $2N$ 次分圆多项式为：
>
>$$
>\phi_{2N}(X) =\phi_{2^{k+1}}(X)=X^{2^k}+1 = X^{N} + 1
>$$

- [规范嵌入](https://en.wikipedia.org/wiki/Embedding)，用于编码和解码。它们具有同构的良好特性，即向量和多项式之间的一对一同态。
- [范德蒙德矩阵](https://en.wikipedia.org/wiki/Vandermonde_matrix) ，这是一类特殊的矩阵，我们将使用它来获得规范嵌入的逆数。

>![image-20251008213832982](https://cdn.jsdelivr.net/gh/hxd77/BlogImage/Blog/image-20251008213832982.png)

如果您想运行笔记本，可以在此 Colab 笔记本中找到它。 [this Colab notebook](https://colab.research.google.com/drive/1C2WlzTh-28GUxobvIQK6Nj5GdfunAlH2?usp=sharing).



## Encoding in CKKS

CKKS 利用整数多项式环的丰富结构作为其明文和密文空间。**尽管如此，数据更常以向量的形式出现，而不是多项式的形式。**

因此，有必要将我们的输入 $z∈\mathbb{C}^{N/2}$ 编码为多项式 $m(X)∈Z[X]/(X^N+1)$ 。

我们将用 $N$ 表示多项式次数模 量的次数，这将是 2 的幂。我们用 $\Phi_M(X)=X^N+1$ 表示第 （$m$） 个分圆多项式（请注意 ）。 $M=2N$ 明文空间将是多项式环 $\mathcal{R}=\mathbb{Z}[X]/(X^N+1)$ 。**让我们用 $\xi_M$ 表示统一 的第 $M$ -次根： $\xi_M=e^{2i\pi/M}$** 。

>例如，对于向量 $z = (z_0, z_1, \dots, z_{N/2-1})$，我们可以将其映射到多项式：
>$$
>m(X) = z_0 + z_1 X + z_2 X^2 + \dots + z_{N/2-1} X^{N/2-1}.
>$$

为了了解我们如何将向量编码为多项式，以及对多项式执行的计算将如何反映在底层向量中，我们将首先尝试一个普通示例，其中我们只需将向量 $z∈\mathbb{C}^N$ 编码为多项式 $m(X)∈\mathbb{C}[X]/(X^N+1)$ 。然后我们将介绍 CKKS 的实际编码，**它采用一个向量 $z\in\mathbb{C}^{N/2}$ ，并将其编码为多项式 $m(X)∈\mathbb{Z}[X]/(X^N+1)$ 。**

## Vanilla Encoding

在这里，我们将介绍将 $z∈\mathbb{C}^N$ 编码 的简单情况 ，**转换为多项式 $m(X)∈\mathbb{C}[X]/(X^N+1)$ 。**

为此，我们将使用 规范嵌入 $\sigma:\mathbb{C}[X]/(X^N+1)\to\mathbb{C}^N$ ，它解码和编码我们的向量。

这个想法很简单：要将多项式 $m(X) $ **解码**为向量 $z$，我们需要在特定值上对该多项式进行求值，**这些特定值将是分圆多项式$\Phi_M(X)=X^N+1$的根**。这 $N$ 个根分别是：
$$
\xi,\xi^3,\ldots,\xi^{2N-1}
$$

>#### 1. **多项式的根：**
>
>我们正在讨论的是多项式 $X^N + 1$，它是一个 **带有 $X^N$ 和常数项的多项式**，我们可以将其写作：
>
>$$X^N + 1 = 0$$
>
>解这个方程，我们得到其 **根**。
>
>#### 2. **单位根的定义：**
>
>首先，考虑复数领域中关于“单位根”的定义。我们说 **单位根** 是那些满足以下方程的复数 $\xi$：
>
>$$\xi^k = 1 \quad \text{其中} \quad k \in \mathbb{Z}$$
>
>在复平面中，单位根是一个 **等距分布** 在单位圆上的点。换句话说，它们是复数 $1$ 在单位圆上均匀分布的根。
>
>#### 3. **根的推导：**
>
>多项式 $X^N + 1$ 实际上是在寻找其 **复数根**。我们可以将它改写为：
>
>$$X^N = -1$$
>
>在复数域中，-1 也可以写作 $e^{i\pi}$，因为 $e^{i\pi} = -1$ 是欧拉公式的一个特殊情况。因此，解方程 $X^N = -1$ 等价于解：
>
>$$X^N = e^{i\pi}$$
>
>所以，我们需要找到所有复数 $X$，使得它们的 $N$-次方是 $e^{i\pi}$。
>
>#### 4. **$X^N + 1 = 0$ 的根：**
>
>根据复数的幂运算性质，解方程 $X^N = -1$ 可以写成：
>
>$$X = e^{\frac{i(\pi + 2k\pi)}{N}} \quad \text{其中} \quad k = 0, 1, 2, \dots, N-1$$（因为$e^{\frac{i(\pi + 2k\pi)}{N}\cdot N}=e^{i(\pi + 2k\pi)}=-1$）
>
>这是因为复数的幂是周期性的，所以我们考虑 $\pi + 2k\pi$ 作为一般解，表示旋转的角度。
>
>具体来说，我们得到了：
>
>$$X = e^{i \frac{(2k+1)\pi}{N}} \quad \text{其中} \quad k = 0, 1, 2, \dots, N-1$$
>
>这些解分别是多项式 $X^N + 1 = 0$ 的 **所有根**。每一个 $k$ 对应一个不同的单位根，它们均匀分布在单位圆上。
>
>（**该分圆多项式的根为n次原语单元根 `(nth primitive roots of unity)` $e^{2i\pi \frac{k}{n}}
>$** ，**其中， $k$ 为不大于 $n$ 的正整数，且 $k$ 与 $n$ 为互质数。**）
>
>#### 5. **为什么是这些根：**
>
>在这段话中提到的根 $\xi, \xi^3, \dots, \xi^{2N-1}$ 是通过选择这些单位根的一部分来定义的。具体而言：
>
>* $\xi$ 是 **第一个单位根**，即 $e^{i \frac{\pi}{N}}$。

因此，为了**解码多项式 $m(X)$**，我们定义 $\sigma(m)=(m(\xi),m(\xi^3),\ldots,m(\xi^{2N-1}))\in\mathbb{C}^N.$。注意，$\sigma$定义了一个同构，这意味着它是一个双射同态，因此任何向量都将被唯一编码为其对应的多项式，反之亦然。

>$\sigma$是解码函数

棘手的部分在于将向量$z\in\mathbb{C}^N$编码为相应的多项式，这意味着要计算逆映射$\sigma^{-1}$。因此，问题在于，给定一个向量$z\in\mathbb{C}^N$，找到一个多项式
$$
m(X)=\sum_{i=0}^{N-1}\alpha_iX^i\in\mathbb{C}[X]/(X^N+1)
$$
使得 
$$
\sigma(m)=(m(\xi),m(\xi^3),\ldots,m(\xi^{2N-1}))=(z_1,\ldots,z_N)
$$
进一步沿着这条思路探究，我们最终得到了以下系统：
$$
\sum_{j=0}^{N-1}\alpha_j(\xi^{2i-1})^j=z_i,\quad i=1,\ldots,N.
$$


这可以看作是一个线性方程：
$$
A\alpha=z
$$


其中，$A$ 是 $(\xi^{2i-1})_{i=1,\ldots,N}$ 的范德蒙矩阵，$\alpha$ 是多项式系数向量，$z$ 是我们想要编码的向量。

因此，我们有$\alpha=A^{-1}z$ 和 $\sigma^{-1}(z)=\sum_{i=0}^{N-1}\alpha_iX^i\in\mathbb{C}[X]/(X^N+1)$ 

>### 1. **解码过程**
>
>首先，解码过程是如何进行的。给定一个多项式 $m(X) \in \mathbb{C}[X]/(X^N + 1)$，我们需要将它映射回一个向量 $z \in \mathbb{C}^N$。
>
>我们使用了一个**规范嵌入**函数 $\sigma$，它定义了如何从多项式 $m(X)$ 解码得到向量 $z$。这个过程是通过在特定的根上对多项式进行求值来实现的。
>
>* 这些特定的根是多项式 $X^N + 1$ 的 **根**，即单位根 $\xi$ 的不同幂次：$\xi, \xi^3, \xi^5, \dots, \xi^{2N-1}$。
>
>* 通过将多项式 $m(X)$ 在这些根上求值，我们得到向量 $z = (z_1, z_2, \dots, z_N)$，其中：
>
>   $$
>   \sigma(m) = (m(\xi), m(\xi^3), \dots, m(\xi^{2N-1})) = (z_1, z_2, \dots, z_N)
>   $$
>   **这样，解码函数 $\sigma$ 将一个多项式 $m(X)$ 映射为向量 $z$。**
>
>
>### 2. **编码过程与逆映射**
>
>对于编码过程，我们面临的是 **逆映射**：给定一个向量 $z \in \mathbb{C}^N$，如何找到一个多项式 $m(X) \in \mathbb{C}[X]/(X^N + 1)$，使得解码后的结果正好是向量 $z$？
>
>为了解决这个问题，我们需要**反向构造多项式** $m(X)$。假设我们已经知道向量 $z = (z_1, z_2, \dots, z_N)$，目标是找出一个多项式 $m(X)$ 使得它在 $\xi, \xi^3, \xi^5, \dots, \xi^{2N-1}$ 这些根上分别给出 $z_1, z_2, \dots, z_N$：
>
>$$
>m(\xi) = z_1, \quad m(\xi^3) = z_2, \quad \dots, \quad m(\xi^{2N-1}) = z_N
>$$
>**把多项式 $m(X)$ 分别在 $X^N + 1$ 的每一个根上求值。这叫做 规范嵌入（canonical embedding）**
>
>这是一个典型的**插值问题**，可以通过 **范德蒙矩阵** 来表示。
>
>#### 线性方程组
>
>我们构造一个线性方程组来求解多项式的系数：
>
>* 给定向量 $z = (z_1, z_2, \dots, z_N)$，我们要求解多项式 $m(X) = \sum_{i=0}^{N-1} \alpha_i X^i$ 的系数 $\alpha = (\alpha_0, \alpha_1, \dots, \alpha_{N-1})$，使得在特定的 $\xi^{2i-1}$ 上，$m(X)$ 的值为 $z_i$。
>
>* 这个问题可以表示为一个线性方程：
>
>   $$
>   \sum_{j=0}^{N-1} \alpha_j (\xi^{2i-1})^j = z_i, \quad i=1, \dots, N
>   $$
>   >$\alpha_0+\alpha_1\xi^1+\alpha_2{\xi^1}^{2}+\alpha_3{\xi^1}^{3}=z_1$
>   >
>   >其余同理
>   
>   或者更简洁地写作：
>   $$
>   A \alpha = z
>   $$
>   
>   >$$
>   >\begin{bmatrix}1&{\xi^1}&{\xi^1}^{2}&{\xi^1}^{3}&\\1&{\xi^3}&{\xi^3}^{2}&{\xi^3}^{3}\\1&{\xi^5}&{\xi^5}^{2}&{\xi^5}^{3}\\1&{\xi^7}&{\xi^7}^{2}&{\xi^7}^{2}&\end{bmatrix}\begin{bmatrix}\alpha_0\\ \alpha_1\\ \alpha_2 \\ \alpha_3 \end{bmatrix}=\begin{bmatrix}z_1\\ z_2\\ z_3\\z_4\end{bmatrix}
>   >$$
>
> 其中，$A$ 是一个由 $\xi^{2i-1}$ 的不同幂次组成的 **范德蒙矩阵**，$\alpha$ 是系数向量，$z$ 是向量 $z_1, z_2, \dots, z_N$。
>
>#### 求解
>
>* 通过解这个方程，我们得到 $\alpha = A^{-1} z$，这给出了多项式 $m(X)$ 的系数。
>
>* 最终，编码函数 $\sigma^{-1}(z)$ 就是通过求解这个方程并得到多项式 $m(X)$：
>
>   $$\sigma^{-1}(z) = \sum_{i=0}^{N-1} \alpha_i X^i$$
>
>   其中，$\alpha$ 是通过解线性方程组 $A \alpha = z$ 得到的系数。







## Example

现在让我们来看一个例子，以便更好地理解我们到目前为止所讨论的内容。

设$M=8,N=\frac{M}{2}=4,\Phi_M(X)=X^4+1$和 $\omega=e^{\frac{2i\pi}{8}}=e^{\frac{i\pi}{4}}$

>$\omega=e^\frac{2i\pi}{M}=e^{\frac{2i\pi}{8}}=e^{\frac{i\pi}{4}}$

我们这里的目标是对以下向量进行编码：$[1,2,3,4]$
以及 $[−1,−2,−3,−4]$ ，对它们进行解码，将它们的多项式相加和相乘，然后对结果进行解码。

![](https://raw.githubusercontent.com/hxd77/BlogImage/master/TyporaImage/20251004224359557.png)

Roots **X**^4 +1 (source: [Cryptography from Rings, HEAT summer school 2016](https://heat-project.eu/School/Chris%20Peikert/slides-heat2.pdf))

正如我们所见，为了解码一个多项式，我们只需要在M次单位根的幂上对其进行求值。这里我们选择$\xi_{M}=\omega=e^{\frac{i\pi}{4}}。$

**一旦我们有了$\xi$和 $M$ ，我们就可以分别定义 $\sigma $及其逆 $σ^{-1}$，即解码和编码。**



## Implementation

现在我们可以继续在Python中实现基础编码器和解码器了。

```python
import numpy as np

#第一步我们设置参数
M=8
N=M//2

#我们设置xi，为了用在我们的计算
xi=np.exp(2*np.pi*1j/M)
print(xi)
#xi=(0.7071067811865476+0.7071067811865475j)
```

>| 部分        | 含义                                        |
>| ----------- | ------------------------------------------- |
>| `np.exp(x)` | 计算 $e^x$（自然指数函数）                  |
>| `2 * np.pi` | 表示 $2\pi$，即一整圈弧度                   |
>| `1j`        | 表示虚数单位 $i = \sqrt{-1}$                |
>| `/ M`       | 除以整数 $M$，即取一圈的 $\frac{1}{M}$ 部分 |
>
>* * *
>
>### 🧮 数学上等价表达式：
>
>$$
>\xi = e^{\frac{2\pi i}{M}}
>$$
>
>这是一个 **M 次单位根**（primitive M-th root of unity）。

```python
from numpy.polynomial import Polynomial
import numpy as np

M=8
N=M//2

class CKKSEncoder:
    """基本的CKKS编码器，用于将复向量编码为多项式。"""

    def __init__(self,M:int):
        """当M为2的幂时编码器的初始化
        ξ是一个M次单位根，它将被用作我们计算的基础。
        """
        self.xi=np.exp(2*np.pi*1j/M)
        self.M=M

        """@staticmethod` 表示这个方法既不需要访问类（`cls`），也不需要访问实例（self），就是一个普通函数，只是放在类的命名空间里。"""
    @staticmethod
    def vandermonde(xi:np.complex128,M:int)->np.array:
        """complex128` 是 NumPy 中复数类型（complex number type）的一种数据类型，  表示一个 64位实部 + 64位虚部 的复数，也就是 总共 128 位（16 字节）"""
        """M是单位根的阶数，返回值是一个 numpy 数组（实际上是二维列表）"""
        """“从单位的m次根计算范德蒙矩阵。”"""
        N=M//2
        matrix=[]
        #我们会生成矩阵的每一行
        for i in range(N):
            #每一行我们选择一个不同的根
            root=xi**(2*i+1)#xi=ξ1,ξ3,ξ5,ξ7
            row=[]

            #然后我们存储次项，生成范德蒙德行列式
            for j in range(N):
                row.append(root**j)
                """范德蒙德行列式：
                    [1,ξ1,ξ1^2,ξ1^3]
                    [1,ξ3,ξ3^2,ξ3^3]
                    [1,ξ5,ξ5^2,ξ5^3]
                    [1,ξ7,ξ7^2,ξ7^3]"""
            matrix.append(row)
        return matrix
        
    def sigma_inverse(self,b:np.array)->Polynomial:
        """“使用M次单位根将向量b编码为多项式。”"""

        #首先，我们创建范德蒙德矩阵
        A=CKKSEncoder.vandermonde(self.xi,M)

        #然后我们求解这个方程组
        coeffs=np.linalg.solve(A,b)#求解Ax=b 这里求解出alpha
        """
        例如：
        2x+y=8
        x+3y=13​ 
        求解x,y的值
        """

        #最后我们输出多项式
        p=Polynomial(coeffs)
        """
        创建多项式
        coeffs = [2, -3, 1]   # 表示 2 - 3x + 1x²
        p = Polynomial(coeffs)
        print(p)
        输出：2.0 - 3.0·x + 1.0·x²
         """
        return p #这里恢复出m(X)
        

    def sigma(self,p:Polynomial)->np.array:
        """通过将多项式应用于M次单位根来对其进行解码。"""
        outputs=[]
        N=self.M//2

        #我们只需将这个多项式应用于这些根上。
        for i in range(N):
            root=self.xi**(2*i+1)
            output=p(root)#把多项式 p 代入 x = root 进行计算，得到对应的函数值。
            outputs.append(output)

        return np.array(outputs)#返回z=[z1,z2,z3,z4]
```

让我们首先对一个向量进行编码，看看它是如何使用实数值进行编码的。

```python
# First we initialize our encoder
encoder = CKKSEncoder(M)

b = np.array([1, 2, 3, 4])
```

现在开始编码

```python
#现在开始编码成多项式
p=encoder.sigma_inverse(b)
print(p)
```

`(2.4999999999999996+0j) - (2.7755575615628914e-16-0.7071067811865472j) x -
(2.2204460492503116e-16-0.49999999999999956j) x**2 +
(2.7755575615628914e-16+0.7071067811865468j) x**3`

现在让我们看看如何从这个多项式中提取我们最初拥有的向量：

```python
b_reconstructed = encoder.sigma(p)
print(b_reconstructed)
```

`[1.+1.11022302e-16j 2.+1.11022302e-16j 3.+5.55111512e-17j
 4.-2.22044605e-16j]`

我们可以看到，重构值和初始向量的值非常接近：

```python
np.linalg.norm(b_reconstructed - b)
```

>### 🧮 一、`np.linalg.norm()` 是什么？
>
>`np.linalg.norm()` 是 **NumPy** 线性代数模块 (`linalg`) 里的“向量范数”函数。  
>简单说，它用来衡量一个向量的“长度”或“大小”。
>
>默认情况下：
>
>```python
>np.linalg.norm(x)
>```
>
>计算的是 **欧几里得范数（2范数）**，即：
>
>$$
>\|x\|_2 = \sqrt{x_1^2 + x_2^2 + \dots + x_n^2}
>$$
>
>### 🧩 二、这句代码的整体逻辑
>
>```python
>np.linalg.norm(b_reconstructed - b)
>```
>
>含义是：
>
>> 计算向量 `b_reconstructed` 和 `b` 之间的差距（误差）的大小。
>
>即：
>
>$$
>\|b_{\text{reconstructed}} - b\|_2
>$$
>它衡量“重建的结果”与“原始数据”之间的误差。

`6.944442800358888e-16`

如前所述，$\sigma$并非随机选择来进行编码和解码的，而是具有许多良好的性质。其中，$\sigma$是一个同构映射，因此多项式上的加法和乘法运算会在编码向量上产生按系数的加法和乘法运算。

σ的同态性质源于$X^N+1=0$ 和 $\xi^N+1=0$这一事实。

现在我们可以开始对多个向量进行编码，看看如何对它们执行同态运算并进行解码。

```python
m1 = np.array([1, 2, 3, 4])
m2 = np.array([1, -2, 3, -4])

p1 = encoder.sigma_inverse(m1)
p2 = encoder.sigma_inverse(m2)
```

我们可以看出，加法是相当简单直接的。

```python
p_add = p1 + p2
print(p_add)
```

`(1.9999999999999996+2.220446049250313e-16j) -
(0.7071067811865468-0.7071067811865475j) x -
(2.2204460492503096e-16+1.9999999999999987j) x**2 +
(0.7071067811865461+0.7071067811865469j) x**3`

不出所料，这里我们看到 $p1+p2$ 能正确解码为 $[2,0,6,0]$。

```python
p_add_reconstructed=encoder.sigma(p_add)
print(p_add_reconstructed)
```

`[ 2.0000000e+00-9.19738868e-17j -8.8817842e-16+2.22044605e-16j
  6.0000000e+00+2.22044605e-16j -4.4408921e-16+0.00000000e+00j]`

因为在进行乘法运算时，我们可能会遇到次数高于 $N$ 的项，所以需要使用$X^N+1$来进行模运算。

要执行乘法运算，我们首先需要定义将要使用的多项式模。

```python
poly_modulo = Polynomial([1,0,0,0,1])
print(poly_modulo)
```

>其实定义的是一个**多项式对象**，它表示的数学式子是：
>
>$$
>1 + x^4
>$$

`1.0 + 0.0 x + 0.0 x**2 + 0.0 x**3 + 1.0 x**4`

现在我们可以进行乘法运算了。

```python
p_mult = p1 * p2 % poly_modulo
print(p_mult)
```

`[  1.+7.21644966e-16j  -4.+8.32667268e-16j   9.-5.27355937e-15j
 -16.-2.60902411e-15j]`

最后，如果我们对其进行解码，就能看到我们得到了预期的结果。

```python
p_mult=encoder.sigma(p_mult)
print(p_mult)
```

`[  1.+7.21644966e-16j  -4.+8.32667268e-16j   9.-5.27355937e-15j
 -16.-2.60902411e-15j]`

>### 加法同态（很直接）
>
>对任意代表多项式 $p,q\in R$，有
>
>$$\sigma(p+q) = \big((p+q)(\xi_k)\big)_{k}  
>= \big(p(\xi_k)+q(\xi_k)\big)_{k}  
>= \sigma(p)+\sigma(q).$$
>
>这是因为评价算子在多项式加法下线性（evaluation 是线性的）。  
>因此，加法同态性直接成立：$\sigma(p+q)=\sigma(p)+\sigma(q)$。
>
>
>
>### 乘法同态（关键点：模掉 $f$ 与根使差为 0）
>
>我们要说明的是：若以模 $f$ 的乘法（即在 $R$ 中的乘法）为 $\cdot$，则
>
>$$\sigma(p\cdot q) = \sigma(p)\odot\sigma(q),$$
>
>其中 $\odot$ 表示按分量相乘（Hadamard product）。
>
>证明思路（代数性质）：
>
>* 在环 $R$ 中，所谓 $p\cdot q$ 实际上是取普通多项式乘积再对 $f$ 取余：记
>  
>    $$r(X) = (p\cdot q)(X) \bmod f(X).$$
>    
>    那么存在多项式 $h(X)$ 使得
>    
>    $$p(X)q(X) = r(X) + f(X)h(X).$$
>* 现在对任意根 $\xi_k$ 代入上式，因为 $f(\xi_k)=0$，得到
>  
>    $$p(\xi_k)q(\xi_k) = r(\xi_k).$$
>    
>    所以第 $k$ 分量 $\sigma(r)_k = p(\xi_k)q(\xi_k)$。
>    
>* 因为 $r$ 就是 $p\cdot q$ 在 $R$ 中的代表，得
>  
>    $$\sigma(p\cdot q) = \big(r(\xi_k)\big)_k = \big(p(\xi_k)q(\xi_k)\big)_k = \sigma(p)\odot\sigma(q).$$
>
>这就是乘法同态的完整理由：**对模多项式的差（被 $f$ 整除的多项式）在 $\xi_k$ 处为 0**，所以把“模 $f$”的多项式乘法拉到各根处，正好变成按分量乘法。

因此，我们可以看出，我们简单的编码器和解码器能够按预期工作，因为它具有同态特性，并且在向量和多项式之间是一一对应的映射。

虽然这是重要的一步，但实际上我们之前有所隐瞒，因为你可能已经注意到，当我们使用编码器σ⁻¹时，多项式具有复系数。因此，尽管编码器和解码器确实具有同态性且是一一对应的，但它们所覆盖的域是$\mathbb{C}^N\to\mathbb{C}[X]/(X^N+1)$。由于我们实际上希望多项式属于$\mathbb{Z}[X]/(X^N+1)$，以便利用整数多项式环的所有特性，因此我们需要确保编码器输出的是具有整数系数而非复系数的多项式。
