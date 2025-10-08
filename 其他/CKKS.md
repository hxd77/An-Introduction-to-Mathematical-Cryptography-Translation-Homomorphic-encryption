**\*\***This post is part of our [Privacy-Preserving Data Science, Explained](https://blog.openmined.org/private-machine-learning-explained/) series.**\*\***

## CKKS explained series

Part 1, Vanilla Encoding and Decoding  
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

- [圆体多项式](https://en.wikipedia.org/wiki/Cyclotomic_polynomial)是具有良好属性的多项式，因为它们在用作多项式模时允许高效计算。
- [规范嵌入](https://en.wikipedia.org/wiki/Embedding)，用于编码和解码。它们具有同构的良好特性，即向量和多项式之间的一对一同态。
- [范德蒙德矩阵](https://en.wikipedia.org/wiki/Vandermonde_matrix) ，这是一类特殊的矩阵，我们将使用它来获得规范嵌入的逆数。

如果您想运行笔记本，可以在此 Colab 笔记本中找到它。 [this Colab notebook](https://colab.research.google.com/drive/1C2WlzTh-28GUxobvIQK6Nj5GdfunAlH2?usp=sharing).

## Encoding in CKKS

CKKS 利用整数多项式环的丰富结构作为其明文和密文空间。尽管如此，数据更常以向量的形式出现，而不是多项式的形式。

因此，有必要将我们的输入 $z∈CN/2$ 编码为多项式 $m(X)∈Z[X]/(X^N+1)$ 。

我们将用 $N$ 表示多项式次数模 量的次数，这将是 2 的幂。我们用 $\Phi_M(X)=X^N+1$ 表示第 （$m$） 个圆体多项式（请注意 ）。 $M=2N$ 明文空间将是多项式环 $\mathcal{R}=\mathbb{Z}[X]/(X^N+1)$ 。让我们用 $\xi_M$ 表示统一 的第 M -次根： $\xi_M=e^{2i\pi/M}$ 。

为了了解我们如何将向量编码为多项式，以及对多项式执行的计算将如何反映在底层向量中，我们将首先尝试一个普通示例，其中我们只需将向量 编码 $z∈\mathbb{C}^N$ 为多项式 $m(X)∈\mathbb{C}[X]/(X^N+1)$ 。然后我们将介绍 CKKS 的实际编码，**它采用一个向量 $z\in\mathbb{C}^{N/2}$ ，并将其编码为多项式 $m(X)∈\mathbb{Z}[X]/(X^N+1)$ 。**

## Vanilla Encoding

在这里，我们将介绍将 $z∈\mathbb{C}^N$ 编码 的简单情况 ，转换为多项式 $m(X)∈\mathbb{C}[X]/(X^N+1)$ 。

为此，我们将使用 规范嵌入 $\sigma:\mathbb{C}[X]/(X^N+1)\to\mathbb{C}^N$ ，它解码和编码我们的向量。

这个想法很简单：要将多项式 $m(X) $ **解码**为向量 $z$，我们需要在特定值上对该多项式进行求值，这些特定值将是分圆多项式$\Phi_M(X)=X^N+1$的根。这 $N$ 个根分别是：$\xi,\xi^3,\ldots,\xi^{2N-1}$

因此，为了**解码多项式 $m(X)$**，我们定义 $\sigma(m)=(m(\xi),m(\xi^3),\ldots,m(\xi^{2N-1}))\in\mathbb{C}^N.$。注意，$\sigma$定义了一个同构，这意味着它是一个双射同态，因此任何向量都将被唯一编码为其对应的多项式，反之亦然。

>$\sigma$是解码函数

棘手的部分在于将向量$z\in\mathbb{C}^N$编码为相应的多项式，这意味着要计算逆映射$\sigma^{-1}$。因此，问题在于，给定一个向量$z\in\mathbb{C}^N$，找到一个多项式$m(X)=\sum_{i=0}^{N-1}\alpha_iX^i\in\mathbb{C}[X]/(X^N+1)$，使得 $\sigma(m)=(m(\xi),m(\xi^3),\ldots,m(\xi^{2N-1}))=(z_1,\ldots,z_N)$。

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

## Example

现在让我们来看一个例子，以便更好地理解我们到目前为止所讨论的内容。

设$M=8,N=\frac{M}{2}=4,\Phi_M(X)=X^4+1$和 $\omega=e^{\frac{2i\pi}{8}}=e^{\frac{i\pi}{4}}$

我们这里的目标是对以下向量进行编码：$[1,2,3,4]$
以及 $[−1,−2,−3,−4]$ ，对它们进行解码，将它们的多项式相加和相乘，然后对结果进行解码。

![](https://raw.githubusercontent.com/hxd77/BlogImage/master/TyporaImage/20251004224359557.png)

Roots **X**^4 +1 (source: [Cryptography from Rings, HEAT summer school 2016](https://heat-project.eu/School/Chris%20Peikert/slides-heat2.pdf))

正如我们所见，为了解码一个多项式，我们只需要在M次单位根的幂上对其进行求值。这里我们选择$\xi_{M}=\omega=e^{\frac{i\pi}{4}}。$

一旦我们有了$\xi$和 $M$ ，我们就可以分别定义 $\sigma $及其逆 $σ^{-1}$，即解码和编码。



## Implementation

Now we can move on to implement the Vanilla Encoder and Decoder in Python.

```python
import numpy as np

# First we set the parameters
M = 8
N = M //2

# We set xi, which will be used in our computations
xi = np.exp(2 * np.pi * 1j / M)
xi
```

`(0.7071067811865476+0.7071067811865475j)`

```python
from numpy.polynomial import Polynomial

class CKKSEncoder:
    """Basic CKKS encoder to encode complex vectors into polynomials."""

    def __init__(self, M: int):
        """Initialization of the encoder for M a power of 2.

        xi, which is an M-th root of unity will, be used as a basis for our computations.
        """
        self.xi = np.exp(2 * np.pi * 1j / M)
        self.M = M

    @staticmethod
    def vandermonde(xi: np.complex128, M: int) -> np.array:
        """Computes the Vandermonde matrix from a m-th root of unity."""

        N = M //2
        matrix = []
        # We will generate each row of the matrix
        for i in range(N):
            # For each row we select a different root
            root = xi ** (2 * i + 1)
            row = []

            # Then we store its powers
            for j in range(N):
                row.append(root ** j)
            matrix.append(row)
        return matrix

    def sigma_inverse(self, b: np.array) -> Polynomial:
        """Encodes the vector b in a polynomial using an M-th root of unity."""

        # First we create the Vandermonde matrix
        A = CKKSEncoder.vandermonde(self.xi, M)

        # Then we solve the system
        coeffs = np.linalg.solve(A, b)

        # Finally we output the polynomial
        p = Polynomial(coeffs)
        return p

    def sigma(self, p: Polynomial) -> np.array:
        """Decodes a polynomial by applying it to the M-th roots of unity."""

        outputs = []
        N = self.M //2

        # We simply apply the polynomial on the roots
        for i in range(N):
            root = self.xi ** (2 * i + 1)
            output = p(root)
            outputs.append(output)
        return np.array(outputs)
```

Let’s first encode a vector and see how it is encoded using real values.

```python
# First we initialize our encoder
encoder = CKKSEncoder(M)

b = np.array([1, 2, 3, 4])
b
```

`array([1, 2, 3, 4])`

Let’s encode the vector now.

```python
p = encoder.sigma_inverse(b)
p
```

`x↦(2.5+4.440892098500626e-16j)+((-4.996003610813204e-16+0.7071067811865479j))x+((-3.4694469519536176e-16+0.5000000000000003j))x^2+((-8.326672684688674e-16+0.7071067811865472j))x^3`

Now let’s see how we can extract the vector we had initially from the polynomial:

```python
b_reconstructed = encoder.sigma(p)
b_reconstructed
```

`array([1.-1.11022302e-16j, 2.-4.71844785e-16j, 3.+2.77555756e-17j,        4.+2.22044605e-16j])`

We can see that the values of the reconstruction and the initial vector are very close.

```python
np.linalg.norm(b_reconstructed - b)
```

`6.944442800358888e-16`

As stated before, σ is not chosen randomly to encode and decode, but it has a lot of nice properties. Among them, σ is an isomorphism, so addition and multiplication on polynomials will result in coefficient wise addition and multiplication on the encoded vectors.

The homomorphic property of σ is due to the fact that XN+1\=0 and ξN+1\=0.

We can now start to encode several vectors, and see how we can perform homomorphic operations on them and decode it.

```python
m1 = np.array([1, 2, 3, 4])
m2 = np.array([1, -2, 3, -4])

p1 = encoder.sigma_inverse(m1)
p2 = encoder.sigma_inverse(m2)
```

We can see that addition is pretty straightforward.

```python
p_add = p1 + p2
p_add
```

`\( x \mapsto (2.0000000000000004 + 1.1102230246251565e-16j) + ((-0.7071067811865477 + 0.707106781186547j)) x + ((2.1094237467877966e-15 - 1.9999999999999996j)) x^2 + ((0.7071067811865466 + 0.707106781186549j)) x^3 \)`

Here as expected, we see that p1+p2 decodes correctly to \[2,0,6,0\].

```python
encoder.sigma(p_add)
```

`array([2.0000000e+00 + 3.25176795e-17j, 4.4408921e-16 - 4.44089210e-16j, 6.0000000e+00 + 1.11022302e-16j, 4.4408921e-16 + 3.33066907e-16j])`

Because when doing multiplication we might have terms whose degree is higher than N, we will need to do a modulo operation using XN+1.

To perform multiplication, we first need to define the polynomial modulus which we will use.

```python
poly_modulo = Polynomial([1,0,0,0,1])
poly_modulo
```

`\( x \mapsto 1.0 + 0.0x + 0.0x^2 + 0.0x^3 + 1.0x^4 \)`

Now we can perform multiplication.

```python
p_mult = p1 * p2 % poly_modulo
```

Finally if we decode it, we can see that we have the expected result.

```python
encoder.sigma(p_mult)
```

`array([ 1. - 8.67361738e-16j, -4. + 6.86950496e-16j, 9. + 6.86950496e-16j, -16. - 9.08301212e-15j])`

Therefore we can see that our simple encoder and decoder works as expected, as it has homomorphic properties and is a one-to-one mapping between vectors and polynomials.

While this is a great step, we have actually lied because if you noticed before, when we used the encoder σ−1 the polynomials had complex coefficients. So while the encoder and decoder were indeed homomorphic and one-to-one, the domains they covered were CN→C\[X\]/(XN+1). Because we actually want polynomials to belong in Z\[X\]/(XN+1) to use all the properties of integer polynomial rings, we thus need to make sure the encoder outputs polynomials with integer coefficients and not complex coefficients.

So I hope you enjoyed this little introduction to encoding complex numbers into polynomials for homomorphic encryption. We will see in the next article how to implement the actual encoder and decoder used in CKKS so stay tuned!