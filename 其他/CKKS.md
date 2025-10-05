**\*\***This post is part of our [Privacy-Preserving Data Science, Explained](https://blog.openmined.org/private-machine-learning-explained/) series.**\*\***

## CKKS explained series

Part 1, Vanilla Encoding and Decoding  
[Part 2, Full Encoding and Decoding](https://blog.openmined.org/ckks-explained-part-2-ckks-encoding-and-decoding/)  
[Part 3, Encryption and Decryption](https://blog.openmined.org/ckks-explained-part-3-encryption-and-decryption/)  
[Part 4, Multiplication and Relinearization](https://blog.openmined.org/ckks-explained-part-4-multiplication-and-relinearization/)  
[Part 5, Rescaling](https://blog.openmined.org/ckks-explained-part-5-rescaling/)

## Introduction

Homomorphic encryption is a promising field which allows computation on encrypted data. This excellent post, [What Is homomorphic Encryption](https://blog.openmined.org/what-is-homomorphic-encryption/), provides a broad explanation of what homomorphic encryption is and what the stakes are for this field of research.

In this series of articles, we will study in depth the Cheon-Kim-Kim-Song (CKKS) scheme, which is first discussed in the paper [Homomorphic Encryption for Arithmetic of Approximate Numbers](https://eprint.iacr.org/2016/421.pdf). CKKS allows us to perform computations on vectors of complex values (thus real values as well). The idea is that we will implement CKKS from scratch in Python and then, by using these crypto primitives, we can explore how to perform complex operations such as linear regression, neural networks, and so on.

![](https://raw.githubusercontent.com/hxd77/BlogImage/master/TyporaImage/20251004224359731.svg+xml)

High level view of CKKS

The figure above provides a high-level view of CKKS. We can see that a message **m**, a vector of values on which we want to perform certain computation, is first encoded into a _plaintext_ polynomial **p(X)** and then encrypted using a public key.

CKKS works with polynomials because they provide a good trade-off between security and efficiency as compared to standard computations on vectors.

Once the message **m** is encrypted into **c**,  a couple of polynomials, CKKS provides several operations that can be performed on it, such as addition, multiplication and rotation.

If we denote a function by **f**, which is a composition of homomorphic operations, then decrypting **c’ = f(c)** with the secret key will yield **p’ = f(p)**. Therefore once we decode it, we will get **m = f(m).**

The central idea to implement a homomorphic encryption scheme is to have homomorphic properties on the _encoder_, _decoder_, _encryptor_ and _decryptor_. This way, operations on _ciphertext_ will be decrypted and decoded correctly and provide outputs as if operations were done directly on _plaintext_.

So in this article we will see how to implement the encoder and the decoder, and in later articles we will continue to implement the encryptor and decryptor to have a homomorphic encryption scheme.

**Preliminaries**

Basic knowledge in linear algebra and ring theory is recommended to have a good understanding of how CKKS is implemented. You can acquaint yourself with these topics using the following links:

- [Introduction to linear algebra](https://math.mit.edu/~gs/linearalgebra/) provides a good basis in linear algebra.
- [Ring theory (Math 113)](https://math.berkeley.edu/~mcivor/math113su16/113ringnotes2016.pdf) is a good resource to learn ring theory.

Specifically for this article, we will rely on the following concepts:

- [Cyclotomic polynomials](https://en.wikipedia.org/wiki/Cyclotomic_polynomial) which are polynomials with nice properties, as they allow efficient computations when used as polynomial modulo.
- [Canonical embedding](https://en.wikipedia.org/wiki/Embedding) which is used for encoding and decoding. They have the nice properties of being isomorphism, i.e. one-to-one homomorphisms between vectors and polynomials.
- [Vandermonde matrices](https://en.wikipedia.org/wiki/Vandermonde_matrix) which are a special class of matrices, which we will use to have the inverse of the canonical embedding.

If you want to run the notebook you can find it in [this Colab notebook](https://colab.research.google.com/drive/1C2WlzTh-28GUxobvIQK6Nj5GdfunAlH2?usp=sharing).

## Encoding in CKKS

CKKS exploits the rich structure of integer polynomial rings for its plaintext and ciphertext spaces. Nonetheless, data comes more often in the form of vectors than in polynomials.

Therefore, it is necessary to encode our input z∈CN/2 into a polynomial m(X)∈Z\[X\]/(XN+1).

We will denote the degree of our polynomial degree modulus by N, which will be a power of 2. We denote the (m)-th [cyclotomic polynomial](https://en.wikipedia.org/wiki/Cyclotomic_polynomial) (note that M\=2N) by ΦM(X)\=XN+1. The plaintext space will be the polynomial ring R\=Z\[X\]/(XN+1). Let us denote by ξM, the M\-th root of unity: ξM\=e2iπ/M.

To understand how we can encode a vector into a polynomial and how the computation performed on the polynomial will be reflected in the underlying vector, we will first experiment with a vanilla example, where we simply encode a vector z∈CN into a polynomial m(X)∈C\[X\]/(XN+1). Then we will cover the actual encoding of CKKS, which takes a vector z∈CN/2, and encodes it in a polynomial m(X)∈Z\[X\]/(XN+1).

## Vanilla Encoding

Here we will cover the simple case of encoding z∈CN, into a polynomial m(X)∈C\[X\]/(XN+1).

To do so, we will use the [canonical embedding](https://en.wikipedia.org/wiki/Embedding) σ:C\[X\]/(XN+1)→CN, which decodes and encodes our vectors.

The idea is simple: To decode a polynomial m(X) into a vector z, we evaluate the polynomial on certain values, which will be the roots of the cyclotomic polynomial ΦM(X)\=XN+1. Those N roots are: ξ,ξ3,…,ξ2N–1.

So to decode a polynomial m(X), we define σ(m)\=(m(ξ),m(ξ3),…,m(ξ2N–1))∈CN. Note that σ defines an isomorphism, which means it is a bijective homomorphism, so any vector will be uniquely encoded into its corresponding polynomial, and vice-versa.

The tricky part is the encoding of a vector z∈CN into the corresponding polynomial, which means computing the inverse σ−1. Hence, the problem is to find a polynomial m(X)\=∑N−1i\=0αiXi∈C\[X\]/(XN+1), given a vector z∈CN, such that σ(m)\=(m(ξ),m(ξ3),…,m(ξ2N–1))\=(z1,…,zN).

Pursuing this thread further, we end up with the following system:

∑j\=0N−1αj(ξ2i–1)j\=zi,i\=1,…,N.

This can be viewed as a linear equation:

Aα\=z

with A the [Vandermonde matrix](https://en.wikipedia.org/wiki/Vandermonde_matrix) of the (ξ2i−1)i\=1,…,N, α the vector of the polynomial coefficients, and z the vector we want to encode.

Therefore we have that: α\=A−1z, and that σ−1(z)\=∑N−1i\=0αiXi∈C\[X\]/(XN+1).

## Example

Let’s now examine an example to better understand what we have discussed so far.

Let M\=8, N\=M2\=4, ΦM(X)\=X4+1, and ω\=e2iπ8\=eiπ4.  
Our goal here is to encode the following vectors: \[1,2,3,4\] and \[−1,−2,−3,−4\], decode them, add and multiply their polynomial and decode it.

![](https://raw.githubusercontent.com/hxd77/BlogImage/master/TyporaImage/20251004224359557.png)

Roots **X**^4 +1 (source: [Cryptography from Rings, HEAT summer school 2016](https://heat-project.eu/School/Chris%20Peikert/slides-heat2.pdf))

As we can see, in order to decode a polynomial, we simply need to evaluate it on powers of an M\-th root of unity. Here we choose ξM\=ω\=eiπ4.

Once we have ξ and M, we can define both σ and its inverse σ−1, respectively the decoding and the encoding.

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