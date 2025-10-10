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
    
encoder=CKKSEncoder(M)
m1=np.array([1,2,3,4])
m2=np.array([1,-2,3,-4])


#加法同态
p1=encoder.sigma_inverse(m1)
p2=encoder.sigma_inverse(m2)
p_add=p1+p2
p_add_reconstructed=encoder.sigma(p_add)
#print(np.real_if_close(p_add_reconstructed, tol=1e-9))
#print(p_add_reconstructed)

#乘法同态
poly_modulo=Polynomial([1,0,0,0,1])#x^4+1
#print(poly_modulo)
p_mult=p1*p2%poly_modulo
p_mult_reconstructed=encoder.sigma(p_mult)
print(p_mult_reconstructed)

