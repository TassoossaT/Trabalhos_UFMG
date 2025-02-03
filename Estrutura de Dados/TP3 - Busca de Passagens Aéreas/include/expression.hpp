#ifndef EXPRESSION_HPP
#define EXPRESSION_HPP

#include <string>
#include <data_Struct.hpp>
#include <date_.hpp>
#include <flight.hpp>

// Declaração da função que avalia expressões simples (sem && ou ||)
DynamicArray evaluateSimpleExpression(const std::string& expr, 
                                        BalancedBinaryTree<std::string>& org, 
                                        BalancedBinaryTree<std::string>& dst, 
                                        BalancedBinaryTree<double>& prc, 
                                        BalancedBinaryTree<int>& sea, 
                                        BalancedBinaryTree<Date>& dep, 
                                        BalancedBinaryTree<Date>& arr, 
                                        BalancedBinaryTree<int>& sto, 
                                        BalancedBinaryTree<double>& dur);

// Declaração da função recursiva para avaliar expressões lógicas
DynamicArray evaluateExpressionRec(const std::string& s, 
                                    BalancedBinaryTree<std::string>& org, 
                                    BalancedBinaryTree<std::string>& dst, 
                                    BalancedBinaryTree<double>& prc, 
                                    BalancedBinaryTree<int>& sea, 
                                    BalancedBinaryTree<Date>& dep, 
                                    BalancedBinaryTree<Date>& arr, 
                                    BalancedBinaryTree<int>& sto, 
                                    BalancedBinaryTree<double>& dur);

#endif // EXPRESSION_HPP
