# The Learning with Errors Problem

在本次调查中，我们介绍了the Learning with Error（LWE）问题。讨论了其性质、难度以及密码学应用。

## 1. 介绍

近年来，由[Reg05]提出的The Learning with Errors（LWE）问题已成为密码学构造中的一个及其通用的基础。它之所以声明远扬，主要是因为它与最坏情况下的格问题是难解的前提下，所有基于它的密码学构造都是安全的。本综述的目的是介绍我们对这一问题理解的最新进展。尽管这里呈现的所有结果（除了附录 A 中的观察结果外）都已在文献中出现过，但我们试图让表述比原始论文中的更简洁一些。有关 LWE 及相关问题的更多信息，请参见一些最近关于格基密码学的综述 [MR08, Pei09b, Mic07, Reg06]。



**LWE. **LWE问题要求在给定关于秘密 $\mathrm{s}\in\mathbb{Z}_q^n$ 的一系列“近似”随机线性方程组的情况下，从中恢复出秘密$s$。例如，输入可能是
$$
\begin{aligned}14s_1+15s_2+5s_3+2s_4&\approx8({\mathrm{mod}}17)\\13s_1+14s_2+14s_3+6s_4&\approx16({\mathrm{mod}}17)\\6s_1+10s_2+13s_3+1s_4&\approx3({\mathrm{mod}}17)\\10s_1+4s_2+12s_3+16s_4&\approx12({\mathrm{mod}}17)\\9s_1+5s_2+9s_3+6s_4&\approx9({\mathrm{mod}}17)\\3s_1+6s_2+4s_3+5s_4&\approx16({\mathrm{mod}}17)\\&\mathrm{:}\\6s_1+7s_2+16s_3+2s_4&\approx3({\mathrm{mod}}17)\end{aligned}
$$
