(ns core.xapply-test
  (:require [clojure.test :refer :all]
            [clojure.core.ex :refer :all]))

(deftest xapply-test-common
  (testing "content filter"
    (is (= [10 20 30 40]
          (xapply vector 10 20 nil 30 40 )))))
          
(deftest xapply-test-json
  (testing "common test"
    (is (= [1 2 3 4 5 6 7 8]
          (xapply vector :json-like 1 [2 3] 4 5 '(6 7) 8)))))        

(deftest xapply-test-nil
  (testing "nil feature test"
    (is (= []
          (xapply vector :sequence nil nil :scalar nil nil)))))        
