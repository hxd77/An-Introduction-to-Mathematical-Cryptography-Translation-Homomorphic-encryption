*   **\*\***This post is part of our [Privacy-Preserving Data Science, Explained](https://blog.openmined.org/private-machine-learning-explained/) series.**\*\***
    
    ## CKKS explained series
    
    [Part 1, Vanilla Encoding and Decoding](https://blog.openmined.org/ckks-explained-part-1-simple-encoding-and-decoding/)  
    Part 2, 完整编码和解码  
    [Part 3, Encryption and Decryption](https://blog.openmined.org/ckks-explained-part-3-encryption-and-decryption/)  
    [Part 4, Multiplication and Relinearization](https://blog.openmined.org/ckks-explained-part-4-multiplication-and-relinearization/)  
    [Part 5, Rescaling](https://blog.openmined.org/ckks-explained-part-5-rescaling/)
    
    ## Introduction
    
    在之前的文章 CKKS 解释：第 1 部分，香草编码和解码，我们了解到，要实现 CKKS 加密方案在加密的复杂向量上进行计算，我们必须首先构建一个编码器和一个解码器，将我们的复向量转换为多项式。
    
    此编码器-解码器步骤是必要的，因为加密、解密和其他机制适用于多项式环。因此，有必要有一种方法将我们的实值向量转换为多项式。
    
    我们还了解到，通过使用典范嵌入$\sigma$（其作用是通过在 $X^N+1$的根上对多项式进行求值来对多项式进行解码），我们能够在$\mathbb{C}[X]$与$\mathbb{C}[X]/(X^N+1)$之间建立一个同构。然而，由于我们希望编码器输出$\mathbb{C}[X]/(X^N+1)$中的多项式，以便利用多项式整数环的结构，因此我们需要对这个初始的简单编码器进行修改，使其能够输出正确环中的多项式。
    
    因此，在本文中，我们将探讨如何实现原始论文《近似数字算术的同态加密》中使用的编码器和解码器，这将是我们从零开始实现CKKS的第一步。
    
    ## CKKS encoding
    
    **与前一篇帖子的不同之处在于，编码多项式的明文空间现在是$\mathcal{R}=\mathbb{Z}[X]/(X^N+1)$，而非$\mathbb{C}[X]/(X^N+1)$，**因此编码值多项式的系数必须是整数系数。然而，我们已经知道，当对$\mathbb{C}^N$中的向量进行编码时，其编码结果不一定具有整数系数。
    
    为了解决这个问题，让我们来看一下实数集$\mathcal{R}$上典范嵌入$\sigma$的图像。
    
    因为实数域$\mathcal{R}$中的多项式具有整数系数，即实系数，并且我们在复根上对它们进行求值，其中一半复根是另一半的共轭复数（参见前图），所以我们得出：
    $$
    \sigma(\mathcal{R})\subseteq\mathbb{H}=\{z\in\mathbb{C}^N:z_j=\overline{z_{-j}}\}.
    $$
    
    >#### 🌱 一、共轭复数的定义
    >
    >如果有一个复数：
    >
    >$$
    >z = a + bi
    >$$
    >其中 $a$ 是实部，$b$ 是虚部（$i^2 = -1$）。
    >
    >它的**共轭复数（conjugate complex number）**定义为：
    >
    >$$
    >\overline{z} = a - bi
    >$$
    >👉 也就是说，**虚部符号取反**。
    >
    >#### 💡 二、常见性质
    >
    >1. **模长相等：**
    >   
    >    $$
    >    |z| = |\overline{z}|
    >    $$
    >    例如：$|3+4i| = 5$，$|3-4i| = 5$。
    >    
    >2. **实部不变，虚部变号：**
    >   
    >    $$
    >    \text{Re}(\overline{z}) = \text{Re}(z), \quad \text{Im}(\overline{z}) = -\text{Im}(z)
    >    $$
    >3. **乘积变实数：**
    >   
    >    $$
    >    z \cdot \overline{z} = a^2 + b^2 = |z|^2
    >    $$
    >4. **加法、乘法保共轭性：**
    >   
    >    $$
    >    \overline{z_1 + z_2} = \overline{z_1} + \overline{z_2}, \quad  
    >    \overline{z_1 z_2} = \overline{z_1}\,\overline{z_2}
    >    $$
    >
    >* * *
    
    
    
    回想一下之前$M=8$之前的照片：
    
    ![](https://openmined.org//wp-content/uploads/2024/11/roots.png)
    
    Roots **X**⁴ + 1 (source: [Cryptography from Rings, HEAT summer school 2016](https://heat-project.eu/School/Chris%20Peikert/slides-heat2.pdf))
    
    从这张图中我们可以看到$\omega^1=\overline{\omega^7}$的共轭，且$\omega^3=\overline{\omega^5}$的共轭。一般来说，由于我们是在XN+1的根上对实多项式进行求值，所以对于任意多项式$m(X)\in\mathcal{R}$，我们也会有
    $$
    m(\xi^j)=\overline{m(\xi^{-j})}=m(\overline{{\xi^{-j}}})
    $$
    因此，$σ(\mathcal{R})$中的任何元素实际上都处于维度为$N/2$的空间中，而非维度为 $N$ 的空间。所以，当我们在CKKS中对向量进行编码时，如果使用大小为 $N/2$ 的复向量，就需要通过复制共轭根的另一半来对它们进行扩展。
    
    This operation, which takes an element of H and projects it to CN/2, is called π in the CKKS paper. Note that this defines an isomorphism as well.
    
    Now we can start with z∈CN/2, expand it using π−1 (note that π projects, π−1 expands), and we get π−1(z)∈H.
    
    A problem that we face is that we cannot directly use σ:R\=Z\[X\]/(XN+1)→σ(R)⊆H, because an element of H is not necessarily in σ(R). σ does define an isomorphism, but only from R to σ(R). To convince yourself that σ(R)≠H, you can notice that R is countable, therefore σ(R) as well, but H is not, as it is isomorphic to CN/2.
    
    This detail is important because it means that we must find a way to project π−1(z) on σ(R). To do so, we will use a technique called “coordinate-wise random rounding”, defined in [A Toolkit for Ring-LWE Cryptography](https://web.eecs.umich.edu/~cpeikert/pubs/toolkit.pdf). This rounding technique allows to round a real x either to ⌊x⌋ or ⌊x⌋+1 with a probability that is higher the closer x is to ⌊x⌋ or ⌊x⌋+1. We will not go into the details of this algorithm, though we will implement it.
    
    The idea is simple, R has an orthogonal Z\-basis {1,X,…,XN−1} and, given that σ is an isomorphism, σ(R) has an orthogonal Z\-basis β\=(b1,b2,…,bN)\=(σ(1),σ(X),…,σ(XN−1)). Therefore, for any z∈H, we will simply project it on β :
    
    z\=∑Ni\=1zibi, with zi\=⟨z,bi⟩∥bi∥2∈R.
    
    Because the basis is orthogonal and not orthonormal, we have zi\=⟨z,bi⟩∥bi∥2. Note that we are using the Hermitian product here: ⟨x,y⟩\=∑Ni\=1xiyi¯¯¯¯. The Hermitian product gives real outputs because we apply it on elements of H; you can compute to convince yourself or notice that you can find an isometric isomorphism between H and RN, therefore inner products in H will yield real outputs.
    
    Finally, once we have the coordinates zi, we simply need to round them randomly, to the higher or the lower closest integer, using the “coordinate-wise random rounding”. This way we will have a polynomial which will have integer coordinates in the basis (σ(1),σ(X),…,σ(XN−1)), therefore this polynomial will belong to σ(R) and the trick is done.
    
    Once we have projected on σ(R), we can apply σ−1 which will output an element of R, which was what we wanted!
    
    One final detail: because the rounding might destroy some significant numbers, we actually need to multiply by Δ\>0 during encoding, and divide by Δ during decoding to keep a precision of 1Δ. To see how this works, imagine you want to round x\=1.4 and you do not want to round it to the closest integer but to the closest multiple of 0.25 to keep some precision. Then, you want to set the scale Δ\=4, which gives a precision of 1Δ\=0.25. Indeed, now when we get ⌊Δx⌋\=⌊4⋅1.4⌋\=⌊5.6⌋\=6. Once we divide it by the same scale Δ, we get 1.5, which is indeed the closest multiple of 0.25 of x\=1.4.
    
    So the final encoding procedure is :
    
    - take an element of z∈CN/2
    - expand it to π−1(z)∈H
    - multiply it by Δ for precision
    - project it on σ(R): ⌊Δ⋅π−1(z)⌉σ(R)∈σ(R)
    - encode it using σ: m(X)\=σ−1(⌊Δ⋅π−1(z)⌉σ(R))∈R
    
    The decoding procedure is much simpler: from a polynomial m(X), we simply get z\=π∘σ(Δ−1⋅m).
    
    ## Implementation
    
    Now that we finally managed to see how the full CKKS encoding and decoding works, let’s implement it! We will use the code we previously used for the Vanilla Encoder and Decoder. The code is available on [this Colab notebook](https://colab.research.google.com/drive/1cdue90Fg_EB5cxxTYcv2_8_XxQnpnVWg?usp=sharing).
    
    For the rest of the article, let’s refactor and build on top of the `CKKSEncoder` class we have created from the previous post. In a notebook environment, instead of redefining the class each time we want to add or change methods, we will simply use `patch_to` from the `fastcore` package from [Fastai](https://github.com/fastai/fastai). This allows us to monkey patch objects that have already been defined. Using `patch_to` is purely for convenience and you could just redefine the `CKKSEncoder` at each cell with the added methods.
    
    ```python
    # !pip3 install fastcore
    
    from fastcore.foundation import patch_to
    ```
    
    ```python
    @patch_to(CKKSEncoder)
    def pi(self, z: np.array) -> np.array:
        """Projects a vector of H into C^{N/2}."""
    
        N = self.M // 4
        return z[:N]
    
    @patch_to(CKKSEncoder)
    def pi_inverse(self, z: np.array) -> np.array:
        """Expands a vector of C^{N/2} by expanding it with its
        complex conjugate."""
    
        z_conjugate = z[::-1]
        z_conjugate = [np.conjugate(x) for x in z_conjugate]
        return np.concatenate([z, z_conjugate])
    
    # We can now initialize our encoder with the added methods
    encoder = CKKSEncoder(M)
    ```
    
    ```python
    z = np.array([0,1])
    encoder.pi_inverse(z)
    ```
    
    `array([0, 1, 1, 0])`
    
    ```python
    @patch_to(CKKSEncoder)
    def create_sigma_R_basis(self):
        """Creates the basis (sigma(1), sigma(X), ..., sigma(X** N-1))."""
    
        self.sigma_R_basis = np.array(self.vandermonde(self.xi, self.M)).T
    
    @patch_to(CKKSEncoder)
    def __init__(self, M):
        """Initialize with the basis"""
        self.xi = np.exp(2 * np.pi * 1j / M)
        self.M = M
        self.create_sigma_R_basis()
    
    encoder = CKKSEncoder(M)
    ```
    
    We can now have a look at the basis σ(1),σ(X),σ(X2),σ(X3).
    
    ```python
    encoder.sigma_R_basis
    ```
    
    `array([[ 1.00000000e+00+0.j, 1.00000000e+00+0.j, 1.00000000e+00+0.j, 1.00000000e+00+0.j],   [ 7.07106781e-01+0.70710678j, -7.07106781e-01+0.70710678j, -7.07106781e-01-0.70710678j, 7.07106781e-01-0.70710678j],   [ 2.22044605e-16+1.j, -4.44089210e-16-1.j, 1.11022302e-15+1.j, -1.38777878e-15-1.j],   [-7.07106781e-01+0.70710678j, 7.07106781e-01+0.70710678j, 7.07106781e-01-0.70710678j, -7.07106781e-01-0.70710678j]])`
    
    Here we will check that elements of Z({σ(1),σ(X),σ(X2),σ(X3)}) are encoded as integer polynomials.
    
    ```python
    # Here we simply take a vector whose coordinates are (1,1,1,1) in the lattice basis
    coordinates = [1,1,1,1]
    
    b = np.matmul(encoder.sigma_R_basis.T, coordinates)
    b
    ```
    
    `array([1.+2.41421356j, 1.+0.41421356j, 1.-0.41421356j, 1.-2.41421356j])`
    
    We can check now that it does encode to an integer polynomial.
    
    ```python
    p = encoder.sigma_inverse(b)
    p
    ```
    
    `x↦(1+2.220446049250313e-16j)+((1+0j))x+((0.9999999999999998+2.7755575615628716e-17j))x^2+((1+2.220446049250313e-16j))x^3`
    
    ```python
    @patch_to(CKKSEncoder)
    def compute_basis_coordinates(self, z):
        """Computes the coordinates of a vector with respect to the orthogonal lattice basis."""
        output = np.array([np.real(np.vdot(z, b) / np.vdot(b,b)) for b in self.sigma_R_basis])
        return output
    
    def round_coordinates(coordinates):
        """Gives the integral rest."""
        coordinates = coordinates - np.floor(coordinates)
        return coordinates
    
    def coordinate_wise_random_rounding(coordinates):
        """Rounds coordinates randomly."""
        r = round_coordinates(coordinates)
        f = np.array([np.random.choice([c, c-1], 1, p=[1-c, c]) for c in r]).reshape(-1)
    
        rounded_coordinates = coordinates - f
        rounded_coordinates = [int(coeff) for coeff in rounded_coordinates]
        return rounded_coordinates
    
    @patch_to(CKKSEncoder)
    def sigma_R_discretization(self, z):
        """Projects a vector on the lattice using coordinate-wise random rounding."""
        coordinates = self.compute_basis_coordinates(z)
    
        rounded_coordinates = coordinate_wise_random_rounding(coordinates)
        y = np.matmul(self.sigma_R_basis.T, rounded_coordinates)
        return y
    
    encoder = CKKSEncoder(M)
    ```
    
    Finally, because there might be loss of precision during the rounding step, we use the scale parameter Δ to achieve a fixed level of precision.
    
    ```python
    @patch_to(CKKSEncoder)
    def __init__(self, M:int, scale:float):
        """Initializes with scale."""
        self.xi = np.exp(2 * np.pi * 1j / M)
        self.M = M
        self.create_sigma_R_basis()
        self.scale = scale
    
    @patch_to(CKKSEncoder)
    def encode(self, z: np.array) -> Polynomial:
        """Encodes a vector by expanding it first to H,
        scaling it, projecting it on the lattice of sigma(R), and performing
        sigma inverse."""
        pi_z = self.pi_inverse(z)
        scaled_pi_z = self.scale * pi_z
        rounded_scale_pi_zi = self.sigma_R_discretization(scaled_pi_z)
        p = self.sigma_inverse(rounded_scale_pi_zi)
    
        # Round afterwards due to numerical imprecision
        coef = np.round(np.real(p.coef)).astype(int)
        p = Polynomial(coef)
        return p
    
    @patch_to(CKKSEncoder)
    def decode(self, p: Polynomial) -> np.array:
        """Decodes a polynomial by removing the scale,
        evaluating on the roots, and projecting it on \( \mathbb{C}^{N/2} \)"""
        rescaled_p = p / self.scale
        z = self.sigma(rescaled_p)
        pi_z = self.pi(z)
        return pi_z
    
    scale = 64
    
    encoder = CKKSEncoder(M, scale)
    ```
    
    We can now see it in action, the full encoder used by CKKS:
    
    ```python
    z = np.array([3 +4j, 2 - 1j])
    z
    ```
    
    `array([3.+4.j, 2.-1.j])`
    
    Now we have an integer polynomial as our encoding.
    
    ```python
    p = encoder.encode(z)
    p
    ```
    
    `x↦160.0+90.0x+160.0x^2+45.0x^3`
    
    And it actually decodes well!
    
    ```python
    encoder.decode(p)
    ```
    
    `array([2.99718446+3.99155337j, 2.00281554-1.00844663j])`
    
    I hope you enjoyed this little introduction to encoding complex numbers into polynomials for homomorphic encryption. We will deep dive into this further in the following articles, so stay tuned!
    
