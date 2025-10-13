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
    
    因为实数域$\mathcal{R}$中的多项式具有整数系数，即实系数，并且我们在复根上对它们进行求值，**其中一半复根是另一半的共轭复数**（参见前图），所以我们得出：
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
    
    >#### 🧩 一、复指数的定义（欧拉公式）
    >
    >欧拉公式告诉我们：
    >
    >$$
    >e^{i\theta} = \cos\theta + i\sin\theta
    >$$
    >
    >* * *
    >
    >#### 🧠 二、取复共轭
    >
    >复共轭的操作是：
    >
    >> 实部不变，虚部变号。
    >
    >也就是说：
    >
    >$$
    >\overline{a + bi} = a - bi
    >$$
    >那么我们对 $e^{i\theta}$ 取共轭：
    >
    >$$
    >\overline{e^{i\theta}} = \overline{\cos\theta + i\sin\theta}= \cos\theta - i\sin\theta
    >$$
    >
    >* * *
    >
    >#### 💡 三、重新写一下这个结果
    >
    >注意：
    >
    >$$
    >\cos\theta - i\sin\theta = e^{-i\theta}
    >$$
    >这又是欧拉公式，只不过角度取了负号。
    >
    >* * *
    >
    >#### ✅ 四、结论
    >
    >于是我们得到：
    >
    >$$
    >\boxed{\overline{e^{i\theta}} = e^{-i\theta}}
    >$$
    >
    >#### 🌟 应用到单位根上
    >
    >对单位根：
    >
    >$$
    >\xi^j = e^{\frac{2\pi i j}{M}}
    >$$
    >取共轭：
    >
    >$$
    >\overline{\xi^j} = \overline{e^{\frac{2\pi i j}{M}}} = e^{-\frac{2\pi i j}{M}} = \xi^{-j}
    >$$
    >
    >* * *
    >
    >#### 🧩 为什么这会导致
    >
    >$$
    >m(\xi^j) = \overline{m(\xi^{-j})}
    >$$
    >
    >
    >
    >假设 $m(X)$ 的系数都是**实数**，即：
    >
    >$$
    >m(X) = a_0 + a_1 X + a_2 X^2 + \cdots + a_n X^n
    >$$
    >
    >
    >那么：
    >
    >$$
    >\overline{m(\xi^{-j})}  
    >= \overline{a_0 + a_1 \xi^{-j} + a_2 (\xi^{-j})^2 + \cdots}  
    >= a_0 + a_1 \overline{\xi^{-j}} + a_2 (\overline{\xi^{-j}})^2 + \cdots
    >$$
    >
    >
    >而我们刚刚证明了：
    >
    >$$
    >\overline{\xi^{-j}} = \xi^{j}
    >$$
    >
    >
    >所以：
    >
    >$$
    >\overline{m(\xi^{-j})}  
    >= a_0 + a_1 \xi^{j} + a_2 (\xi^{j})^2 + \cdots = m(\xi^{j})
    >$$
    
    回想一下之前$M=8$之前的照片：
    
    ![](https://openmined.org//wp-content/uploads/2024/11/roots.png)
    
    Roots **X**⁴ + 1 (source: [Cryptography from Rings, HEAT summer school 2016](https://heat-project.eu/School/Chris%20Peikert/slides-heat2.pdf))
    
    从这张图中我们可以看到$\omega^1= e^{\frac{i\pi}{4}}  =\overline{\omega^7}=\overline{e^{\frac{7i\pi}{4}}}=e^{\frac{-7i\pi}{4}}$的共轭，且$\omega^3=\overline{\omega^5}$的共轭。一般来说，由于我们是在$X^N+1$的根上对实多项式进行求值，所以对于任意多项式$m(X)\in\mathcal{R}$，我们也会有
    $$
    m(\xi^j)=\overline{m(\xi^{-j})}=m(\overline{{\xi^{-j}}})
    $$
    >#### 🧩 化简角度（单位圆上等价）
    >
    >注意：复指数中角度是**模 $2\pi$** 等价的。  
    >也就是说：
    >$$
    >e^{i\theta} = e^{i(\theta + 2\pi k)} \quad (\forall k \in \mathbb{Z})
    >$$
    >于是：
    >
    >$$
    >e^{-\frac{7i\pi}{4}} = e^{i(-\frac{7\pi}{4} + 2\pi)} = e^{i\frac{\pi}{4}}
    >$$
    >
    >* * *
    >
    >#### ✅ 结论
    >
    >$$
    >\overline{\omega^7} = e^{-\frac{7i\pi}{4}} = e^{i\frac{\pi}{4}} = \omega^1
    >$$
    
    因此，$σ(\mathcal{R})$中的任何元素实际上都处于维度为$N/2$的空间中，而非维度为 $N$ 的空间。所以，当我们在CKKS中对向量进行编码时，如果使用大小为 $N/2$ 的复向量，就需要通过复制共轭根的另一半来对它们进行扩展。
    
    >#### 出发点：评价表示（σ）和共轭对称性回顾
    >
    >* 我们把多项式（模 $X^N+1$）通过评价映射映成长度 $N$ 的复向量：
    >  
    >    $$
    >    \sigma(m) = \big(m(\xi^1), m(\xi^3), \dots, m(\xi^{2N-1})\big)\in\mathbb{C}^N,
    >    $$
    >    其中这些取值点成共轭对（上一半是下半的共轭）。
    >    
    >* 若 $m(X)$ 的系数是 **实数**，那么评价向量满足共轭对称性：
    >  
    >    $$
    >    z_j = \overline{z_{-j}}.
    >    $$
    >    换句话说，向量的后一半由前一半唯一决定 —— 自由度只剩下前一半。  
    >    因此，$\sigma(m)$ 实际上落在集合
    >    
    >    $$
    >    \mathbb{H}=\{z\in\mathbb{C}^N:\; z_j=\overline{z_{-j}}\},
    >    $$
    >    这个集合与 $\mathbb{C}^{N/2}$ 同构（自由度等价），所以“有效维度”为 $N/2$。
    
    这项操作接收$\mathbb{H}$中的一个元素并将其投影到$\mathbb{C}^{N/2}$，在CKKS论文中被称为$\pi$。请注意，这也定义了一种同构。
    
    现在我们可以从$z\in\mathbb{C}^{N/2}$开始，利用$\pi^{-1}$对其进行扩展（注意，$\pi$是投影，$\pi^{-1}$是扩展），这样我们就得到$\pi^{-1}(z)\in\mathbb{H}$。
    
    >#### 扩展操作（$\pi^{-1}$）：怎么把 $v$ 变成 $Z$
    >
    >* 定义投影 $\pi:\mathbb{H}\to\mathbb{C}^{N/2}$ 为“取前半段”，即 $\pi(Z)=(Z_0,\dots,Z_{N/2-1})，v=(Z_0,\dots,Z_{N/2-1)})$.
    >  
    >* 它的一个逆（扩展）$\pi^{-1}:\mathbb{C}^{N/2}\to\mathbb{H}$ 可以自然定义为：
    > $$
    >    \pi^{-1}(v) = Z,\quad\text{其中 } Z_j = v_j \ (0\le j < N/2),\quad Z_{-j} = \overline{v_j}.(-j\equiv N-j(\mod N))
    > $$
    >    也就是说：把你给的 $N/2$ 个复数放到向量的前半部分，后一半填入对应的共轭值。结果显然满足 $Z\in\mathbb{H}$。
    >    
    >
    >**举例（$N=8$）**：若 $v=(a,b,c,d)$（长度 $4$），则
    >$$
    >\pi^{-1}(v) = Z=(a,b,c,d,\overline{d},\overline{c},\overline{b},\overline{a}).\\v=(Z_0,\dots,Z_{N/2-1)})=(a,b,c,d)
    >$$
    
    我们面临的一个问题是，我们不能直接使用$σ:\mathcal{R}=Z[X]/(X^N+1)→σ(\mathcal{R})⊆\mathbb{H}，$，因为$\mathbb{H}$中的元素不一定在$σ(R)$中。$σ$ 确实定义了一个同构，但只是从$\mathcal{R}$到   $σ(\mathcal{R})$的同构。要确信$\sigma(\mathcal{R})\neq\mathbb{H}$，你可以注意到$\mathcal{R}$是可数的，因此$σ(\mathcal{R})$也是可数的，但$\mathbb{H}$不是可数的，因为它与$\mathbb{C}^{N/2}$同构。
    
    >#### 🧩 一、σ 是什么？
    >
    >在 CKKS 里，
    >
    >$$
    >\sigma: \mathcal{R} = \mathbb{Z}[X]/(X^N + 1) \;\longrightarrow\; \mathbb{C}^N
    >$$
    >是一个**代数同构**，它把多项式
    >
    >$$
    >m(X) = a_0 + a_1 X + a_2 X^2 + \dots + a_{N-1} X^{N-1}
    >$$
    >映射到它在 $X^N + 1 = 0$ 的所有复根处的取值：
    >
    >$$
    >\sigma(m) = \big(m(\xi^0),\, m(\xi^1),\, m(\xi^2),\, \dots,\, m(\xi^{N-1})\big),
    >$$
    >其中 $\xi = e^{i\pi/N}$。
    >
    >* * *
    >
    >#### 🧠 二、σ 的值域是 σ(ℛ)，而不是整个 ℍ
    >
    >我们知道：
    >
    >$$
    >\sigma(\mathcal{R}) \subseteq \mathbb{H} = \{z \in \mathbb{C}^N \mid z_j = \overline{z_{-j}}\}
    >$$
    >也就是说：
    >
    >* ℍ 是所有满足「共轭对称」的复向量集合；
    >  
    >* σ($\mathcal{R}$) 只是其中一小部分，是**那些由整数系数多项式生成的点值**。
    >  
    >
    >* * *
    >
    >#### 📏 三、为什么 σ(ℛ) ≠ ℍ？
    >
    >因为这两个集合的“大小”完全不同：
    >
    >| 集合                        | 内容                     | 是否可数                       |
    >| --------------------------- | ------------------------ | ------------------------------ |
    >| $\mathcal{R}$ = ℤ[X]/(Xⁿ+1) | 系数都是整数的多项式     | ✅ 可数的                       |
    >| σ($\mathcal{R}$)            | 多项式在根处的取值结果   | ✅ 可数的（因为它来自 ℛ）       |
    >| ℍ                           | 满足共轭对称的所有复向量 | ❌ 不可数的（因为包含连续复数） |
    >
    
    这一细节很重要，因为它意味着我们必须找到一种方法将$\pi^{-1}(z)$投影到$σ(\mathcal{R})$上。为了实现这一点，我们将使用一种名为“按坐标随机舍入”的技术，该技术在《环-LWE密码学工具包》（https://web.eecs.umich.edu/~cpeikert/pubs/toolkit.pdf）中有定义。这种舍入技术能够将实数$x$舍入到$\lfloor x\rfloor$ 或 $\lfloor x\rfloor+1$，且$x$ 越接近$\lfloor x\rfloor$ 或 $\lfloor x\rfloor+1$，舍入到对应值的概率就越高。我们不会深入探讨该算法的细节，但会对其进行实现。
    
    这个想法很简单，$\mathcal{R}$ 有一个正交 $\mathbb{Z}\text{ -基}\left\{1,X,\ldots,X^{N-1}\right\}$，并且由于$σ$是一个同构映射，$σ(\mathcal{R})$ 有一个正交 $\mathbb{Z}\text{ -基 }\beta=(b_1,b_2,\ldots,b_N)=(\sigma(1),\sigma(X),\ldots,\sigma(X^{N-1}))\mathrm{~。}$。因此，对于任意 $z\in\mathbb{H}$，我们只需将其投影到 $β$ 上：
    
    $$
    \begin{gathered}\\z=\sum_{i=1}^Nz_ib_i\text{ ,与 }z_i=\frac{\langle z,b_i\rangle}{\left\|b_i\right\|^2}\in\mathbb{R}\mathrm{~。}\end{gathered}
    $$
    
    >##### 🧠 应用到你提到的多项式空间
    >
    >在你的例子中，空间是：
    >
    >$$
    >\mathcal{R} = \mathbb{Z}[X]/(X^N+1)
    >$$
    >也就是**模多项式 $X^N + 1$** 的**多项式环**。
    >
    >在这个空间中，任意一个元素都可以写成：
    >
    >$$
    >a_0 + a_1 X + a_2 X^2 + \cdots + a_{N-1} X^{N-1}
    >$$
    >其中每个 $a_i \in \mathbb{Z}$。
    >
    >因此，集合：
    >
    >$$
    >\{1, X, X^2, \dots, X^{N-1}\}
    >$$
    >就构成了 $\mathcal{R}$ 的一个 **$\mathbb{Z}$-基底**，  
    >因为：
    >
    >* 任意多项式都能由它们线性组合表示；
    >  
    >* 它们彼此线性无关。
    >  
    >
    
    >#### 🧮 一、为什么它们是正交的
    >
    >我们要看的是这些列向量 $b_i$ 之间的内积：
    >
    >$$
    >\langle b_i, b_j \rangle = \sum_{k=1}^N \omega_k^{i-1} \overline{\omega_k^{j-1}}(埃尔米特积)
    >$$
    >利用共轭的性质 $\overline{\omega_k^{j-1}} = \omega_k^{-(j-1)}$，得：
    >
    >$$
    >\langle b_i, b_j \rangle = \sum_{k=1}^N \omega_k^{i-j}
    >$$
    >现在关键点来了：这其实就是一个**几何级数求和**。
    >
    >* 当 $i = j$ 时，$\omega_k^{i-j} = 1$，所以：
    >  
    >    $$
    >    \langle b_i, b_i \rangle = \sum_{k=1}^N 1 = N
    >    $$
    >    
    >* 当 $i \ne j$ 时，$\omega_k^{i-j}$ 是单位根的不同幂的和。由于单位根均匀分布在单位圆上，它们的和为 **0**：
    >  
    >    $$
    >    \sum_{k=1}^N \omega_k^{i-j} = 0
    >    $$
    >    
    >* 
    >
    >#### ✅ 二、结论
    >
    >因此我们有：
    >
    >$$
    >\langle b_i, b_j \rangle =  
    >\begin{cases}  
    >N, & i = j \\  
    >0, & i \ne j  
    >\end{cases}
    >$$
    >
    >
    >这正是**正交基底（orthogonal basis）**的定义。  
    >（注意它们不是**标准正交（orthonormal）**的，因为模长是 $\sqrt{N}$，不是 1。）
    >
    >#### 🧭 直观解释（几何角度）
    >
    >想象单位圆上均匀分布的 8 个点（例如 $N=8$）：
    >
    >* 当 $i=j$，每个点的相位角相同，所有项都是 1，相加得到 $8$。
    >  
    >* 当 $i\ne j$，这些相位角有规律地旋转一圈，相加方向相互抵消，结果为 0。
    >  
    >
    >所以这组向量两两正交。
    >
    >* * *
    >
    >
    >
    >#### ⚙️ 四、把任意 z 投影到 β 上
    >
    >现在我们有一个向量 $z \in \mathbb{H}$，  
    >想找到一个最接近它的向量在 σ(ℛ) 中。
    >
    >因为 $β$ 是 $σ(\mathcal{R})$ 的基底，任何向量 $z'\in\sigma(\mathcal{R})$ 都可以写成：
    >
    >$$
    >z' = \sum_{i=1}^{N} z_i b_i
    >$$
    >为了得到系数 $z_i$，我们对 $z$ 在这些基底上**做正交投影**：
    >
    >$$
    >z_i = \frac{\langle z, b_i \rangle}{\|b_i\|^2}
    >$$
    >这里的 $\langle \cdot, \cdot \rangle$ 是**埃尔米特内积（Hermitian inner product）**，定义为：
    >
    >$$
    >\langle x, y \rangle = \sum_{k=1}^{N} x_k \, \overline{y_k}.
    >$$
    
    由于基底是正交的而非标准正交的，我们有$z_i=\frac{\langle z,b_i\rangle}{\left\|b_i\right\|^2}$。注意，这里我们使用的是埃尔米特积：$\langle x,y\rangle=\sum_{i=1}^Nx_i\overline{y_i}$。埃尔米特积会给出实数值输出，因为我们将其应用于H中的元素；你可以通过计算来验证这一点，或者注意到可以找到$\mathbb{H}$与$\mathbb{R}^{N}$之间的一个等距同构，因此$\mathbb{H}$中的内积将产生实数值输出。
    
    最后，一旦我们得到坐标 $z_i$，只需使用“逐坐标随机舍入”的方法，将它们随机舍入到较高或较低的最近整数。这样，我们就会得到一个在基 $(\sigma(1),\sigma(X),\ldots,\sigma(X^{N-1}))$ 中具有整数坐标的多项式，因此该多项式将属于$σ(\mathcal{R})$，整个技巧就完成了。
    
    一旦我们在$σ(\mathcal{R})$上进行了投影，就可以应用 $σ⁻¹$ ，它会输出 $\mathcal{R}$ 中的一个元素，这正是我们想要的！
    
    **最后一个细节：由于舍入可能会丢失一些有效数字，我们实际上需要在编码时乘以$Δ＞0$，并在解码时除以 $Δ$，以保持 $1/Δ$ 的精度。**为了理解这一原理，假设你要对 $x=1.4$进行舍入，且不想将其舍入到最接近的整数，而是舍入到最接近的 $0.25$ 的倍数以保留一定精度。这时，你需要设置缩放因子 $Δ=4$，这样精度就是 $1/Δ=0.25$。实际上，此时计算 $⌊Δx⌋=⌊4·1.4⌋=⌊5.6⌋=6$。当我们用同一个缩放因子 $Δ$ 除这个结果时，得到 $1.5$ ，这确实是 $x=1.4$ 最接近的 $0.25$ 的倍数。
    
    
    
    >#### 🧩 1️⃣ 背景：为什么要「缩放」？
    >
    >在 CKKS 编码中，我们把实数（或复数）编码成整数多项式系数。  
    >但是多项式的系数只能是**整数**（属于 $\mathbb{Z}$ 或 $\mathbb{Z}_q$），  
    >而我们的明文 $x$ 通常是实数，比如 $1.4, 3.14159, -2.718$。
    >
    >所以我们必须把实数“变成整数”才能编码。  
    >👉 这就是 **缩放（scaling）** 的作用。
    >
    >* * *
    >
    >#### 🧩 2️⃣ 原理：乘上 Δ，使实数变大后再取整
    >
    >我们引入一个**缩放因子** $\Delta > 0$，  
    >把实数 $x$ 放大成：
    >$$
    >x' = \Delta \cdot x
    >$$
    >然后我们对 $x'$ 取整（或随机舍入），得到整数：
    >
    >$$
    >\tilde{x} = \text{round}(x')
    >$$
    >再把这个整数存入明文多项式。
    >
    >* * *
    >
    >#### 🧩 3️⃣ 解码时：再除回 Δ
    >
    >解码时，我们做相反的操作：  
    >把整数系数除以 Δ，就能得到原来的近似值：
    >
    >$$
    >x \approx \frac{\tilde{x}}{\Delta}
    >$$
    >这样我们就实现了“**实数 → 整数 → 实数近似还原**”的过程。
    >
    >* * *
    >
    >#### 🧮 4️⃣ 用你的例子来直观理解
    >
    >> “假设你要对 $x=1.4$ 进行舍入，且不想将其舍入到最接近的整数，而是舍入到最接近的 $0.25$ 的倍数以保留一定精度。”
    >
    >👉 我们希望结果只能是：
    >
    >$$
    >\{0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, \ldots\}
    >$$
    >这意味着：**精度是 0.25**，也就是
    >
    >$$\text{精度} = \frac{1}{\Delta} = 0.25 \Rightarrow \Delta = 4$$
    >
    >* * *
    >
    >#### ✅ 编码阶段：
    >
    >$$
    >\Delta x = 4 \times 1.4 = 5.6
    >$$
    >
    >取整：
    >
    >$$
    >\tilde{x} = \lfloor 5.6 \rfloor = 6
    >$$
    >
    >#### ✅ 解码阶段：
    >
    >$$
    >x_{\text{decoded}} = \frac{\tilde{x}}{\Delta} = \frac{6}{4} = 1.5
    >$$
    >
    >* * *
    >
    >#### 🧠 5️⃣ 为什么这是“最接近的 0.25 的倍数”
    >
    >因为我们让“整数网格”乘以 $1/\Delta$ 就变成了
    >
    >$$
    >\{0, 0.25, 0.5, 0.75, \ldots\}
    >$$
    >换句话说：
    >
    >* 我们不再以整数为单位舍入；
    >  
    >* 而是以 $1/\Delta$ 为单位舍入。
    >  
    >
    >也就是说，**Δ 决定了你要保留多少小数精度。**
    
    因此，最终的编码步骤如下：
    
    + 取$z\in\mathbb{C}^{N/2}$中的一个元素
    + 将其扩展为$\pi^{-1}(z)\in\mathbb{H}$
    + 为保证精度，将其乘以 $Δ$
    + 将其投影到 $\sigma(\mathcal{R}){:}\lfloor\Delta\cdot\pi^{-1}(z)\rceil_{\sigma(\mathcal{R})}\in\sigma(\mathcal{R})$
    + 使用$\sigma:m(X)=\sigma^{-1}(\left\lfloor\Delta\cdot\pi^{-1}(z)\right\rceil_{\sigma(\mathcal{R})})\in\mathcal{R}$对其进行编码：
    
    解码步骤则简单得多：从多项式 $m(X)$ 出发，我们只需得到$\mid z=\pi\circ\sigma(\Delta^{-1}\cdot m)\mathrm{~。}$
    
    ## Implementation
    
    既然我们终于弄清楚了完整的CKKS编码和解码是如何工作的，那我们就来实现它吧！我们将使用之前用于Vanilla编码器和解码器的代码。该代码可在这个[Colab](https://colab.research.google.com/drive/1cdue90Fg_EB5cxxTYcv2_8_XxQnpnVWg?usp=sharing)笔记本中获取。
    
    在本文的其余部分，让我们基于上一篇文章中创建的`CKKSEncoder`类进行重构和扩展。在笔记本环境中，为了避免每次想要添加或修改方法时都重新定义该类，我们将直接使用`Fastai`的`fastcore`包中的 `patch_to` 。这使我们能够对已定义的对象进行猴子补丁（动态修改）。使用 `patch_to` 纯粹是为了方便，你也可以在每个单元格中重新定义带有新增方法的 `CKKSEncoder`。
    
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
