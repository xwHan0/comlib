(ns core.xupdate-test
  (:require [clojure.test :refer :all]
            [clojure.core.ex :refer :all]))

(deftest xupdate-test
  (testing "content filter"
    (is (= {:width [450 450 450 450 500 600]}
          (xupdate {:width [100 200 300 400 500 600]} [:width #(< %2 500)] 450))))

  (testing "pred filter"
    (let [c [{:a "x" :b 100} {:a "y" :b 200} {:a "z" :b 300}]
          r [{:a "x" :b 100} {:a "y" :b 400} {:a "z" :b 300}]]
      (is (= r
            (xupdate c [#(-> %2 :a #{"y"}) :b] + 200)))))
)
          
          