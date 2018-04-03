(ns core.concat-distinct-test
  (:require [clojure.test :refer :all]
            [clojure.core.ex :refer :all]))

(deftest concat-distinct-test
  (testing "Basic test"
    (is (= [1 2 3 4 5 6 7 8 9 10]
          (concat-distinct [1 2 3 4 5 6] [4 3 6 7 8 2 9 1 10])))      
  )
  
)