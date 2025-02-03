#include <string>
#include <iostream>
#include "data_Struct.hpp"
#include "date_.hpp"
#include "flight.hpp"
#include "expression.hpp"

DynamicArray evaluateSimpleExpression(const std::string& expr, 
                                        BalancedBinaryTree<std::string>& org, 
                                        BalancedBinaryTree<std::string>& dst, 
                                        BalancedBinaryTree<double>& prc, 
                                        BalancedBinaryTree<int>& sea, 
                                        BalancedBinaryTree<Date>& dep, 
                                        BalancedBinaryTree<Date>& arr, 
                                        BalancedBinaryTree<int>& sto, 
                                        BalancedBinaryTree<double>& dur) 
{
    // Identificar o operador pela lista
    std::string op;
    size_t pos = std::string::npos;
    const std::string operators[] = {"==", "!=", "<=", ">=", "<", ">"};
    for (const auto& candidate : operators) {
        pos = expr.find(candidate);
        if (pos != std::string::npos) {
            op = candidate;
            break;
        }
    }
    if(op.empty()) {
        return DynamicArray();
    }
    
    // Extrair field e value, removendo espaços
    std::string field = expr.substr(0, pos);
    std::string valueStr = expr.substr(pos + op.size());
    auto trim = [](std::string s) {
        size_t start = s.find_first_not_of(" \t");
        size_t end   = s.find_last_not_of(" \t");
        return (start == std::string::npos) ? "" : s.substr(start, end - start + 1);
    };
    field = trim(field);
    // Remover parênteses externos se presentes (caso o campo esteja completamente cercado)
    if(!field.empty() && field.front()=='(' && field.back()==')')
        field = field.substr(1, field.size()-2);
    // Adicional: remover quaisquer parênteses residuais no início ou fim 
    while(!field.empty() && (field.front()=='(' || field.front()==')'))
        field.erase(field.begin());
    while(!field.empty() && (field.back()=='(' || field.back()==')'))
        field.pop_back();
    
    valueStr = trim(valueStr);
    // Remover parênteses residuais no final de valueStr
    while(!valueStr.empty() && (valueStr.back()=='(' || valueStr.back()==')'))
        valueStr.pop_back();
    
    // Converter field para enum (usando lambda auxiliar)
    enum FieldType { ORG, DST, PRC, SEA, DEP, ARR, STO, DUR, UNKNOWN };
    auto getFieldType = [&](const std::string& f) -> FieldType {
        if(f == "org") return ORG;
        if(f == "dst") return DST;
        if(f == "prc") return PRC;
        if(f == "sea") return SEA;
        if(f == "dep") return DEP;
        if(f == "arr") return ARR;
        if(f == "sto") return STO;
        if(f == "dur") return DUR;
        return UNKNOWN;
    };

    FieldType type = getFieldType(field);
    DynamicArray result;

    switch(type) {
        case ORG: {
            DynamicArray res = org.getIndices(valueStr, op);
            return res;
        }
        case DST: {
            DynamicArray res = dst.getIndices(valueStr, op);
            return res;
        }
        case PRC: {
            double val = std::stod(valueStr);
            DynamicArray res = prc.getIndices(val, op);
            return res;
        }
        case SEA: {
            int val = std::stoi(valueStr);
            DynamicArray res = sea.getIndices(val, op);
            return res;
        }
        case DEP: {
            Date val = Date::fromString(valueStr);
            DynamicArray res = dep.getIndices(val, op);
            return res;
        }
        case ARR: {
            Date val = Date::fromString(valueStr);
            DynamicArray res = arr.getIndices(val, op);
            return res;
        }
        case STO: {
            int val = std::stoi(valueStr);
            DynamicArray res = sto.getIndices(val, op);
            return res;
        }
        case DUR: {
            double val = std::stod(valueStr);
            DynamicArray res = dur.getIndices(val, op);
            return res;
        }
        default:
            break;
    }
    
    return result;
}

DynamicArray evaluateExpressionRec(const std::string& s, 
                                    BalancedBinaryTree<std::string>& org, 
                                    BalancedBinaryTree<std::string>& dst, 
                                    BalancedBinaryTree<double>& prc, 
                                    BalancedBinaryTree<int>& sea, 
                                    BalancedBinaryTree<Date>& dep, 
                                    BalancedBinaryTree<Date>& arr, 
                                    BalancedBinaryTree<int>& sto, 
                                    BalancedBinaryTree<double>& dur) 
{
    // Caso base: expressão simples (não contém && ou ||)
    if (s.find("&&") == std::string::npos && s.find("||") == std::string::npos) {
        return evaluateSimpleExpression(s, org, dst, prc, sea, dep, arr, sto, dur);
    }
    
    // Remove parênteses externos se houver
    std::string expr = s;
    if(expr.front() == '(' && expr.back() == ')') {
        expr = expr.substr(1, expr.size() - 2);
    }
    
    int balance = 0;
    size_t opPos = std::string::npos;
    std::string op;
    // Percorre a string caractere a caractere para encontrar o operador lógico de nível externo
    for (size_t i = 0; i < expr.size() - 1; ++i) {
        if (expr[i] == '(') {
            balance++;
        } else if (expr[i] == ')') {
            balance--;
        }
        // Quando o balanço volta a 0, estamos em nível externo
        if (balance == 0) {
            std::string possibleOp = expr.substr(i + 1, 2);
            if (possibleOp == "&&" || possibleOp == "||") {
                opPos = i + 1;
                op = possibleOp;
                break;
            }
        }
    }
    
    // Se não encontrou operador de nível externo, trate como expressão simples
    if (opPos == std::string::npos) {
        return evaluateSimpleExpression(expr, org, dst, prc, sea, dep, arr, sto, dur);
    }
    
    // Divide a expressão em trecho esquerdo (s1) e trecho direito (s2)
    std::string s1 = expr.substr(0, opPos);
    std::string s2 = expr.substr(opPos + 2);
    
    DynamicArray leftResult = evaluateExpressionRec(s1, org, dst, prc, sea, dep, arr, sto, dur);
    DynamicArray rightResult = evaluateExpressionRec(s2, org, dst, prc, sea, dep, arr, sto, dur);
    
    // Combina os resultados com base no operador lógico
    if (op == "&&") {
        return leftResult && rightResult;
    } else if (op == "||") {
        return leftResult || rightResult;
    }
    
    // Retorna array vazio em caso de operador desconhecido
    return DynamicArray();
}
