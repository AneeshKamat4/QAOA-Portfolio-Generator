from django.shortcuts import render
from .models import stocks
from .utils import *

from django.http import HttpResponse
from django.template import loader

import numpy as np
import json
import datetime
import math
import random

#Global Variables
stock_names = ['AAPL', 'AMZN', 'FB', 'GOOG', 'MSFT']
cov_mat = np.array([[1.0, 0.5, 0.3, 0.4, 0.2], [0.5, 1.0, 0.2, 0.3, 0.1], [0.3, 0.2, 1.0, 0.5, 0.4], [0.4, 0.3, 0.5, 1.0, 0.6], [0.2, 0.1, 0.4, 0.6, 1.0]])
curr_price = [['AAPL', 100], ['AMZN', 100], ['FB', 100], ['GOOG', 100], ['MSFT', 100]]
user_bias = [0, 1, 0, 1, 0, 1]
pConvergence = 0.9
user_budget = 1000
final_res = [0, 1, 0, 1, 0, 1]


def is_ajax(request):
  return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def calc_cov(stock_names, date_st, date_end):
  lst_st = []
  for i in stock_names:
    temp = stocks.objects.filter(stock_name=i, date__range=[date_st.date(), date_end.date()]).values()
    lst_st.append(temp)
  Stc = np.empty((len(lst_st[0]), len(lst_st)))
  for i in range(len(lst_st)):
    for j in range(len(lst_st[i])):
      Stc[j][i] = lst_st[i][j]['stock_price']
  mu = np.mean(Stc, axis=0)
  M = Stc - mu
  Mt = M.transpose()
  cov_mat = np.matmul(Mt, M) 
  cov_mat /= len(lst_st[0])
  return cov_mat

def rand_arr(len):
  arr1 = []
  arr2 = []
  n_elem = max(math.floor(0.25*len), 1)
  n_elem1 = n_elem - math.floor(random.random()*n_elem)
  n_elem2 = n_elem - n_elem1
  for i in range(n_elem1):
    arr1.append(math.floor(random.random()*len))
  for i in range(n_elem2):
    arr2.append(math.floor(random.random()*len))
  ret = []
  for i in range(len):
    if i in arr1:
      ret.append(1)
    elif i in arr2:
      ret.append(0)
    else:
      ret.append(2)
  return ret
  


def index(request):
  template = loader.get_template('stocks.html')  
  context = {
    'stocks': stock_names,
    'cov_mat': cov_mat,
    'curr_price': curr_price,
    'final_res': final_res
  }
  return HttpResponse(template.render(context, request))

def st(request):
  if is_ajax(request) and request.method == 'POST':
    #print(request.body)
    global stock_names, cov_mat, curr_price
    msg = json.loads(request.body)
    date_st = datetime.datetime.strptime(msg[-2], "%Y-%m-%d")
    date_end = datetime.datetime.strptime(msg[-1], "%Y-%m-%d")
    stock_names = []
    for i in range(len(msg)-2):
      stock_names.append(msg[i])
    cov_mat = calc_cov(stock_names, date_st, date_end)
    curr_price = []
    for i in stock_names:
      temp = stocks.objects.filter(stock_name=i, date__range=[date_st, date_end]).values()
      curr_price.append([i, float(temp[0]['stock_price'])])
    #print(cov_mat, curr_price, stock_names)
    bias_arr = rand_arr(len(stock_names))
    ret_msg = {'cov_mat': cov_mat.tolist(), 'curr_price': curr_price, 'stock_names': stock_names, 'bias_arr': bias_arr}
    return HttpResponse(json.dumps(ret_msg), content_type='application/json')
  else:
    return HttpResponse('error')

def calc(request) :
  if is_ajax(request) and request.method == 'POST':
    global final_res, stock_names, cov_mat, curr_price, user_bias, pConvergence, user_budget
    msg = json.loads(request.body)
    #print(msg)
    method = msg[2]
    cov_mat = [list( map(float,i) ) for i in cov_mat]
    user_budget = float(msg[1])
    user_bias = msg[0]
    user_bias = [int(i) for i in user_bias]
    price_list = [i[1] for i in curr_price]
    price_list = [float(i) for i in price_list]
    pConvergence = float(msg[3])/100
    if method == 'QA':
      final_res = optimal_allocation_anneal(cov_mat, price_list, user_budget, user_bias, pConvergence).tolist()
    else :
      final_res = QAOA(cov_mat, price_list, user_budget, user_bias, pConvergence).tolist()
    resp = {
      'final_res': final_res,
      'stock_names': stock_names,
      'bias_arr': user_bias
    }
    return HttpResponse(json.dumps(resp), content_type='application/json')
  else:
    return HttpResponse('error')