from fastcore.foundation import patch_to #fastapi的patch_to用法：https://chatgpt.com/c/68ece14d-656c-8324-af67-4c22ec0e0859
from numpy.polynomial import Polynomial
import numpy as np

class CKKSEncoder:
    """基本的CKKS编码器，用于将复向量编码为多项式。"""

    def __init__(self,M:int):
        """初始化scale"""
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
        coeffs=np.linalg.solve(A,b)#求解Ax=b 这里求解出alpha=(a0,a1,a2,a3)，可以构造多项式
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

@patch_to(CKKSEncoder)
def pi(self,z:np.array)->np.array:
    """pi:将H向量投影到C^{N/2}中。因为M=2N,所以M/4=N/2"""
    N2=self.M//4
    return z[:N2]

@patch_to(CKKSEncoder)
def pi_inverse(self,z:np.array)->np.array:
    """通过用其复共轭对一个C^{N/2}向量进行扩展，从而将该向量展开。"""

    z_conjugate=z[::-1]#翻转z
    z_conjugate=[np.conjugate(x) for x in z_conjugate]#取共轭
    return np.concatenate((z,z_conjugate))#拼接


@patch_to(CKKSEncoder)
def create_sigma_R_basis(self):
    #创建基（sigma(1)，sigma(X)，…，sigma(X**N-1)）。
    self.sigma_R_basis=np.array((self.vandermonde(self.xi,self.M))).T
    """
    [[1, ξ1, ξ1^2, ..., ξ1^(N/2-1)],
    [1, ξ3, ξ3^2, ..., ξ3^(N/2-1)],
    ...].T代表转置

    """
 
"""
    sigma_R_basis的结构如下：
    | 行/列  | col 0 = σ(1) | col1 = σ(X) | col2 = σ(X²) | col3 = σ(X³) |
    | ---- | ------------ | ----------- | ------------ | ------------ |
    | row0 | 1+0j         | 1+0j        | 1+0j         | 1+0j         |
    | row1 | ξ1           | ξ3          | ξ5           | ξ7           |
    | row2 | ξ1²          | ξ3²         | ξ5²          | ξ7²          |
    | row3 | ξ1³          | ξ3³         | ξ5³          | ξ7³          |
    每个列向量代表一个基 β=(σ(1),σ(X),σ(X2),σ(X3))
"""
"""
矩阵乘向量按 **行向量 dot 坐标向量**：

$$b_i = \sum_{j=0}^{3} (\sigma\_R\_basis.T)_{ij} \cdot coordinates[j]$$
代入你给的矩阵和 `[1,1,1,1]`：
* **行 0**：
$$b_0 = 1\cdot 1 + ξ_1\cdot 1 + ξ_1^2\cdot 1 + ξ_1^3\cdot 1 = 1 + ξ_1 + ξ_1^2 + ξ_1^3$$
* **行 1**：
$$b_1 = 1 + ξ_3 + ξ_3^2 + ξ_3^3$$
* **行 2**：
$$b_2 = 1 + ξ_5 + ξ_5^2 + ξ_5^3$$
* **行 3**：
$$b_3 = 1 + ξ_7 + ξ_7^2 + ξ_7^3$$
所以 `b` 就是 **每一行元素的和**，每行和对应一个复数。
其实这里的coordinates=[1,1,1,1]就是alpha=(a0,a1,a2,a3)
"""

@patch_to(CKKSEncoder)
def compute_basis_coordinates(self,z)->np.array:
    """计算向量相对于正交晶格基的坐标。"""
    output=np.array([np.real(np.vdot(z,b)/np.vdot(b,b)) for b in self.sigma_R_basis])
    """
    sigma_R_basis的结构如下：
    [[1+0j,1+0j,1+0j,1+0j],
    [ξ1,ξ3,ξ5,ξ7],
    [ξ1²,ξ3²,ξ5²,ξ7²],
    [ξ1³,ξ3³,ξ5³,ξ7³]]
    """
    """np.vdot(a, b) 计算两个向量 a 和 b 的埃米特内积，其中 a 的共轭转置与 b 相乘。
    z_i = \frac{\langle z, b_i \rangle}{\|b_i\|^2}
    """
    return output#返回zi


def round_coordinates(coordinates):
    """将坐标四舍五入到最接近的整数。"""
    coordinates=coordinates-np.floor(coordinates)
    return coordinates
    #x↦x−⌊x⌋



def coordinate_wise_random_rounding(coordinates):
    """随机对坐标进行取整"""
    r=round_coordinates(coordinates)
    f=np.array([np.random.choice([c,c-1],1,p=[1-c,c])for c in r]).reshape(-1)
    """
    np.array([1.2,2.8]):
    假设r = [0.2, 0.8]
    | c   | 可能结果       | 概率(选 c) | 概率(选 c-1) | 实际取值可能             |
    | --- | ------------- | ------- | --------- | ------------------ |
    | 0.2 | `[0.2, -0.8]` | 0.8     | 0.2       | 大多数取 0.2，小概率取 -0.8 |
    | 0.8 | `[0.8, -0.2]` | 0.2     | 0.8       | 大多数取 -0.2，小概率取 0.8 |
    1代表1个样本，可能返回[0.2,-0.2]或[0.2,0.8]或[-0.8,-0.2]或[-0.8,0.8](reshape(-1)展开成一维数组)
    """

    rounded_coordinates=coordinates-f#上面的例子：rounded_coordinates=[1.2,2.8]-[0.2,-0.2]=[1,3]
    rounded_coordinates=[int(coeff)for coeff in rounded_coordinates]#取整
    return rounded_coordinates

@patch_to(CKKSEncoder)
def sigma_R_discretization(self,z):
    """使用逐坐标随机舍入将向量投影到格上。"""
    coordinates=self.compute_basis_coordinates(z)#计算zi

    rounded_coordinates=coordinate_wise_random_rounding(coordinates)#对zi进行随机取整
    y=np.matmul(self.sigma_R_basis.T,rounded_coordinates)#z=\sum zi*bi
    #y=2σ(1)+0σ(X)+2σ(X2)+0σ(X3)返回z值
    return y


@patch_to(CKKSEncoder)
def __init__(self,M:int,scale:float):
    """初始化编码器，创建基并设置缩放因子。"""
    self.xi=np.exp(2*np.pi*1j/M)
    self.M=M
    self.scale=scale
    self.create_sigma_R_basis()

@patch_to(CKKSEncoder)
def encode(self,z:np.array)->Polynomial:
    """通过先将向量扩展到H、对其进行缩放、将其投影到sigma(R)的格上并执行sigma逆运算，来对该向量进行编码。"""
    pi_z=self.pi_inverse(z)#扩展z
    scaled_pi_z=pi_z*self.scale#z乘上scale,这里z是消息
    rounded_scale_pi_z=self.sigma_R_discretization(scaled_pi_z)#投影到格上
    p=self.sigma_inverse(rounded_scale_pi_z)#sigma逆运算，得到多项式
    
    #由于数值不精确，稍后进行四舍五入
    coef=np.round(np.real(p.coef)).astype(int)#取实部，四舍五入，转为整数
    """
    coef用法:取出p的系数
    p = Polynomial([1.2 + 0.8j, -2.3 + 0.1j, 3.7 - 0.5j])
    # array([ 1.2+0.8j, -2.3+0.1j, 3.7-0.5j ])
    real取实部，round四舍五入，astype(int)转为整数
    """
    p=Polynomial(coef)
    return p

@patch_to(CKKSEncoder)
def decode(self,p:Polynomial)->np.array:
    """通过去除scale、在根上求值并将其投影到\( \mathbb{C}^{N/2} \)上来对多项式进行解码"""
    rescaled_p=p/self.scale#去除scale
    z=self.sigma(rescaled_p)#在根上求值
    pi_z=self.pi(z)#投影到C^{N/2}上
    return pi_z

scale=64
M=8
encoder=CKKSEncoder(M,scale)

z=np.array([3+4j,2-1j])

p=encoder.encode(z)
p_decode=encoder.decode(p)
print(p)
print(p_decode)
print(encoder.pi_inverse(p_decode))