(ns core.ex-test
  (:require [clojure.test :refer :all]
            [clojure.core.ex :refer :all]))

; #_(deftest xsub-position-test

;   (testing "xsub-position-type test"
;     (is (= (xsub 1 [1 2 3]) 2))
;     (is (= (xsub 3 "hanxwei") \x))
;     (is (= (xsub 2 '(1 2 3)) 3))
;     (is (= (xsub 0 #{1 2 3}) 1))
;     (is (= (xsub 1 {:a 1 :b 2}) [:b 2])))

;   (testing "xsub-position test"
;     (is (= (xsub -1 [1 2 3]) 3))
;     (is (= (xsub :SUB-CFG {:default-val 100} -5 [1 2 3]) 100))
;     )

;   (testing "xsub-map test"
;     (is (= (xsub :SUB-MAP 1 [1 2 3]) nil))
;     (is (= (xsub :SUB-MAP :a {:a 1 :b 2}) 1))))

; #_(deftest xsub-test

;   #_(testing "sub default"
;     (is (= (xsub [1 2 3]) 1))
;     (is (= (xsub 1 [2 3 4]) 3))))

; (deftest xapply-test
  
;   (testing "xapply test"
;     (is (= [1 2 3] (xapply vector 1 2 3)))
;     (is (= '(1 2 3) (xapply list 1 2 3)))
;     (is (= #{1 2 3} (xapply hash-set 1 2 3)))
;     (is (= [1 2 3] (xapply vector 1 nil 2 nil 3)))
;     (is (= [1 2 3 4 5 6] (xapply vector 1 :sequence [2 3] :scalar 4 :sequence '(5 6))))
;     #_(is (= [1 2 nil 3] (xapply :cfg {:ignore-nil? false} 1 2 nil 3)))))

; (deftest test-hiccup2clj
  
;   (testing "Basic function"
    
;     (is (= {:a 100 :b 200} (hiccup2clj [:test {:a 100 :b 200}])))
    
;     (is (= {:sub [1 2 3]} (hiccup2clj [:test [:sub 1 2 3]])))
    
;     (is (= {:sub [{:a 100 :b 200}]} (hiccup2clj [:test [:sub {:a 100 :b 200}]])))
    
;     (is (= {:name "soi"
;             :description ["hello","world"]
;             :signal [{:name "vld"}
;                      {:name "info"}]
;             :scen [{:name "ETH"
;                     :field [{:name "cos"}
;                             {:name "tp"}]}
;                    {:name "NG"
;                     :field [{:name "fclass"}]}]}
           
;            (hiccup2clj [:test {:name "soi"}
;                         [:description "hello" "world"]
;                         [:signal {:name "vld"}]
;                         [:signal {:name "info"}]
;                         [:scen {:name "ETH"}
;                          [:field {:name "cos"}]
;                          [:field {:name "tp"}]]
;                         [:scen {:name "NG"}
;                          [:field {:name "fclass"}]]])))))

; (deftest test-xupdate
;   (testing "Basic test"
;     (is (= {:a 100 :b 200} (xupdate {:a 100 :b 100} :b #(+ % 100))))
;     (is (= {:a 200 :b 200} (xupdate {:a 100 :b 100} :a #(+ % 100) :b #(+ % 100))))))